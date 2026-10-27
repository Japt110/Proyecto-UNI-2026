"""
===============================================================================
EVENTOS-UNI - API REST DE REGISTRO DE ASISTENCIA (`/api/asistencia`)
===============================================================================
Proporciona endpoints RESTful para la toma e inspección de asistencias:
- POST /api/asistencia/<evento_id> : Registro atómico con validación en padrón.
- GET  /api/asistencia/<evento_id> : Listado detallado de personas asistentes.
- POST /api/asistencia/persona-nueva : Registro de Estudiantes / Trabajadores nuevos.
===============================================================================
"""

import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session
from sqlalchemy import func
from database import db
from models.eventos import Asistencia, Actividad
from models.base import Persona, Estudiante, Trabajador, Usuario
from models.catalogos import Sede, UnidadOrganizativa, Ciudad
from core.security import login_required
from extensions import cache

asistencia_bp = Blueprint("asistencia_api", __name__)


# -----------------------------------------------------------------------------
# 1. POST /api/asistencia/<evento_id> - Registro Atómico de Asistencia
# -----------------------------------------------------------------------------

@asistencia_bp.route("/<string:evento_id>", methods=["POST"])
@login_required
def registrar_asistencia(evento_id: str):
    """
    Registra la asistencia de una Persona a una Actividad específica.
    Búsqueda polimórfica en padrón (Cédula, NUP, Carné o Código de Trabajador),
    con o sin guiones, con prevención estricta de marcas dobles.
    """
    data = request.get_json()
    if not data or not data.get("identifier"):
        return jsonify({"success": False, "message": "Identificador de persona requerido"}), 400

    raw_id = data.get("identifier").strip()
    clean_id = raw_id.replace('-', '').replace(' ', '').upper()

    # 1. Validar existencia de la actividad y verificar que las asistencias estén abiertas
    actividad = Actividad.query.get(evento_id)
    if not actividad:
        return jsonify({"success": False, "message": "El evento no existe"}), 404

    if not getattr(actividad, 'asistencia_abierta', True):
        return jsonify({"success": False, "message": "La toma de asistencia para esta actividad se encuentra cerrada"}), 400

    # 2. Búsqueda polimórfica tolerante a guiones (Cédula, NUP, Carné o Código de Trabajador)
    persona = Persona.query.filter(
        (Persona.numero_unico == raw_id) |
        (Persona.cedula == raw_id) |
        (func.replace(Persona.numero_unico, '-', '') == clean_id) |
        (func.replace(Persona.cedula, '-', '') == clean_id)
    ).first()

    if not persona:
        estudiante = Estudiante.query.filter(
            (Estudiante.carnet_estudiante == raw_id) |
            (func.replace(Estudiante.carnet_estudiante, '-', '') == clean_id)
        ).first()
        if estudiante:
            persona = estudiante.persona

    if not persona:
        trabajador = Trabajador.query.filter(
            (Trabajador.codigo_trabajador == raw_id) |
            (func.replace(Trabajador.codigo_trabajador, '-', '') == clean_id)
        ).first()
        if trabajador:
            persona = trabajador.persona

    if not persona:
        return jsonify({"success": False, "not_found": True, "message": "La persona no está registrada en el padrón universitario"}), 404

    # 3. Prevenir marcas dobles de asistencia en la misma actividad
    asistencia_existente = Asistencia.query.filter_by(
        actividad_id=evento_id, persona_id=persona.id
    ).first()

    if asistencia_existente:
        return jsonify({
            "success": False,
            "message": f"Atención: {persona.nombres_apellidos} ya registró asistencia previamente"
        }), 409

    # 4. Inserción atómica de la marca de Asistencia
    registrador_id = session.get("user_id")
    if not registrador_id:
        usr = Usuario.query.first()
        if usr: registrador_id = usr.id

    nueva_asistencia = Asistencia(
        id=data.get("id") or str(uuid.uuid4()),
        actividad_id=evento_id,
        persona_id=persona.id,
        usuario_registrador_id=registrador_id,
        timestamp_registro=data.get("timestamp_registro") or datetime.now(timezone.utc).isoformat(),
        is_synced=data.get("is_synced", 1)
    )

    db.session.add(nueva_asistencia)
    db.session.commit()

    # Invalidar caché de estadísticas y conteos tras nueva marca de asistencia
    cache.clear()

    grupo_estudiante = persona.estudiante.grupo if persona.estudiante else "N/A"

    return jsonify({
        "success": True,
        "message": "Asistencia registrada correctamente",
        "asistente": {
            "nombre": persona.nombres_apellidos,
            "numero_unico": persona.numero_unico,
            "cedula": persona.cedula,
            "grupo": grupo_estudiante,
            "tipo_persona": "Estudiante" if persona.estudiante else ("Trabajador" if persona.trabajador else "General")
        }
    }), 201


# -----------------------------------------------------------------------------
# 2. POST /api/asistencia/<evento_id>/toggle-estado - Abrir / Cerrar Asistencias
# -----------------------------------------------------------------------------

@asistencia_bp.route("/<string:evento_id>/toggle-estado", methods=["POST"])
@login_required
def toggle_estado_asistencia(evento_id: str):
    """Conmuta el estado de apertura/cierre de la asistencia de una actividad sin finalizar el evento."""
    actividad = Actividad.query.get(evento_id)
    if not actividad:
        return jsonify({"success": False, "message": "El evento no existe"}), 404

    actividad.asistencia_abierta = not getattr(actividad, 'asistencia_abierta', True)
    db.session.commit()
    cache.clear()

    estado_str = "abiertas" if actividad.asistencia_abierta else "cerradas"
    return jsonify({
        "success": True,
        "asistencia_abierta": actividad.asistencia_abierta,
        "message": f"Asistencias {estado_str} correctamente"
    }), 200


# -----------------------------------------------------------------------------
# 3. GET /api/asistencia/<evento_id> - Listado de Asistentes del Evento (26 Columnas)
# -----------------------------------------------------------------------------

@asistencia_bp.route("/<string:evento_id>", methods=["GET"])
@login_required
def listar_asistentes(evento_id: str):
    """Retorna la lista de todas las personas asistidas a un evento con sus 26 campos normalizados."""
    actividad = Actividad.query.get(evento_id)
    if not actividad:
        return jsonify({"success": False, "message": "Evento no encontrado"}), 404

    asistencias = Asistencia.query.filter_by(actividad_id=evento_id).all()
    resultado = []

    for a in asistencias:
        persona = a.persona
        est = persona.estudiante if persona else None
        trab = persona.trabajador if persona else None

        grupo = est.grupo if est else "N/A"
        carrera = est.carrera if est else (trab.cargo if trab else "General")
        ano_academico = est.ano_academico if est else "N/A"
        turno = est.turno if est else "Diurno"

        sede_nombre = persona.sede.nombre if (persona and persona.sede) else "RUSB"
        dept_sede = "Managua"
        mun_sede = "Managua"
        if persona and persona.sede and persona.sede.ciudad:
            mun_sede = persona.sede.ciudad.nombre
            if persona.sede.ciudad.departamento:
                dept_sede = persona.sede.ciudad.departamento.nombre

        mun_res = persona.ciudad_residencia.nombre if (persona and getattr(persona, 'ciudad_residencia', None) and persona.ciudad_residencia) else "Managua"
        dept_res = persona.ciudad_residencia.departamento.nombre if (persona and getattr(persona, 'ciudad_residencia', None) and persona.ciudad_residencia and persona.ciudad_residencia.departamento) else "Managua"

        mun_proc = persona.ciudad_procedencia.nombre if (persona and getattr(persona, 'ciudad_procedencia', None) and persona.ciudad_procedencia) else "Managua"
        dept_proc = persona.ciudad_procedencia.departamento.nombre if (persona and getattr(persona, 'ciudad_procedencia', None) and persona.ciudad_procedencia and persona.ciudad_procedencia.departamento) else "Managua"

        resultado.append({
            "id": a.id,
            "numero_unico": persona.numero_unico if persona else "N/A",
            "nombres_apellidos": persona.nombres_apellidos if persona else "Desconocido",
            "sexo": persona.sexo if persona else "Masculino",
            "edad": 21,
            "nacionalidad": "Nicaragüense",
            "pais_procedencia": "Nicaragua",
            "etnia": "Mestizo",
            "departamento_procedencia": dept_proc,
            "municipio_procedencia": mun_proc,
            "departamento_residencia": dept_res,
            "municipio_residencia": mun_res,
            "tipo_ingreso": "Regular",
            "sede": sede_nombre,
            "departamento_sede": dept_sede,
            "municipio_sede": mun_sede,
            "programa_especial": "Ninguno",
            "departamento_unicam": "N/A",
            "municipio_unicam": "N/A",
            "nivel_formacion": "Grado",
            "carrera": carrera,
            "area": "DACTIC",
            "duracion_carrera": "5 Años",
            "ano_academico": ano_academico,
            "regimen": "Semestral",
            "modalidad": "Presencial",
            "turno": turno,
            "grupo": grupo,
            "timestamp_registro": a.timestamp_registro,
            "is_synced": a.is_synced
        })

    return jsonify({
        "success": True,
        "total": len(resultado),
        "asistencia_abierta": getattr(actividad, 'asistencia_abierta', True),
        "evento": {
            "id": actividad.id,
            "nombre": actividad.nombre,
            "codigo": actividad.codigo_actividad,
            "status": actividad.calcular_status()
        },
        "asistentes": resultado
    }), 200


# -----------------------------------------------------------------------------
# 4. GET /api/asistencia/buscar-estudiantes - Buscador Tolerante a Guiones
# -----------------------------------------------------------------------------

@asistencia_bp.route("/buscar-estudiantes", methods=["GET"])
@login_required
def buscar_estudiantes():
    """Buscador polimórfico y filtrado tolerante a guiones para el modo manual de toma de asistencias."""
    query = request.args.get("query", "").strip()
    cedula = request.args.get("cedula", "").strip()
    nup = request.args.get("nup", "").strip()
    carnet = request.args.get("carnet", "").strip()
    nombre = request.args.get("nombre", "").strip()
    carrera = request.args.get("carrera", "").strip()
    grupo = request.args.get("grupo", "").strip()

    clean_q = query.replace('-', '').replace(' ', '').upper() if query else ""

    q = db.session.query(Persona).outerjoin(Estudiante, Persona.id == Estudiante.persona_id)

    if query:
        q = q.filter(
            (Persona.nombres_apellidos.ilike(f"%{query}%")) |
            (Persona.cedula.ilike(f"%{query}%")) |
            (Persona.numero_unico.ilike(f"%{query}%")) |
            (Estudiante.carnet_estudiante.ilike(f"%{query}%")) |
            (func.replace(Persona.cedula, '-', '').ilike(f"%{clean_q}%")) |
            (func.replace(Persona.numero_unico, '-', '').ilike(f"%{clean_q}%")) |
            (func.replace(Estudiante.carnet_estudiante, '-', '').ilike(f"%{clean_q}%"))
        )
    if cedula:
        clean_ced = cedula.replace('-', '').upper()
        q = q.filter(
            (Persona.cedula.ilike(f"%{cedula}%")) |
            (func.replace(Persona.cedula, '-', '').ilike(f"%{clean_ced}%"))
        )
    if nup:
        clean_nup = nup.replace('-', '').upper()
        q = q.filter(
            (Persona.numero_unico.ilike(f"%{nup}%")) |
            (func.replace(Persona.numero_unico, '-', '').ilike(f"%{clean_nup}%"))
        )
    if carnet:
        clean_car = carnet.replace('-', '').upper()
        q = q.filter(
            (Estudiante.carnet_estudiante.ilike(f"%{carnet}%")) |
            (func.replace(Estudiante.carnet_estudiante, '-', '').ilike(f"%{clean_car}%"))
        )
    if nombre:
        q = q.filter(Persona.nombres_apellidos.ilike(f"%{nombre}%"))
    if carrera:
        q = q.filter(Estudiante.carrera.ilike(f"%{carrera}%"))
    if grupo:
        q = q.filter(Estudiante.grupo.ilike(f"%{grupo}%"))

    personas = q.limit(50).all()
    resultados = []

    for p in personas:
        est = p.estudiante
        trab = p.trabajador
        resultados.append({
            "id": p.id,
            "numero_unico": p.numero_unico,
            "cedula": p.cedula,
            "nombres_apellidos": p.nombres_apellidos,
            "sexo": p.sexo,
            "sede": p.sede.nombre if p.sede else "Sede Central",
            "carnet": est.carnet_estudiante if est else (trab.codigo_trabajador if trab else "N/A"),
            "carrera": est.carrera if est else (trab.cargo if trab else "N/A"),
            "grupo": est.grupo if est else "N/A",
            "ano_academico": est.ano_academico if est else "N/A",
            "turno": est.turno if est else "N/A",
            "tipo": "Estudiante" if est else ("Trabajador" if trab else "General")
        })

    return jsonify({"success": True, "total": len(resultados), "estudiantes": resultados}), 200


# -----------------------------------------------------------------------------
# 5. POST /api/asistencia/persona-nueva & /estudiante-nuevo (Persona Nueva)
# -----------------------------------------------------------------------------

@asistencia_bp.route("/persona-nueva", methods=["POST"])
@asistencia_bp.route("/estudiante-nuevo", methods=["POST"])
@login_required
def registrar_persona_nueva():
    """Registra una Persona Nueva en la BD (Estudiante o Trabajador) y marca su asistencia si se especifica el evento."""
    data = request.get_json() or {}

    tipo_persona = (data.get("tipo_persona") or "Estudiante").strip()
    nup = (data.get("nup") or "").strip()
    cedula = (data.get("cedula") or "").strip()
    nombres_apellidos = (data.get("nombres_apellidos") or "").strip()
    sexo = (data.get("sexo") or "Masculino").strip()
    ciudad_residencia_id = data.get("ciudad_residencia_id")
    ciudad_procedencia_id = data.get("ciudad_procedencia_id")

    # Campos específicos de Estudiante
    carnet = (data.get("carnet") or nup or cedula).strip()
    carrera = (data.get("carrera") or "Ingeniería de Sistemas").strip()
    grupo = (data.get("grupo") or "1M1-SO").strip()
    ano_academico = (data.get("ano_academico") or "1º Año").strip()
    turno = (data.get("turno") or "Diurno").strip()

    # Campos específicos de Trabajador
    codigo_trabajador = (data.get("codigo_trabajador") or nup or cedula).strip()
    cargo = (data.get("cargo") or "Docente").strip()
    tipo_contrato = (data.get("tipo_contrato") or "Tiempo Completo").strip()

    evento_id = data.get("evento_id")

    if not nombres_apellidos:
        return jsonify({"success": False, "message": "El nombre completo de la persona es requerido"}), 400
    if not cedula and not nup and not carnet and not codigo_trabajador:
        return jsonify({"success": False, "message": "Se requiere al menos Cédula, NUP, Carné o Código"}), 400

    # Auto-generar identificadores si alguno falta
    if not nup: nup = carnet or codigo_trabajador or f"NUP-{uuid.uuid4().hex[:8].upper()}"
    if not cedula: cedula = f"CED-{uuid.uuid4().hex[:8].upper()}"
    if not carnet: carnet = nup
    if not codigo_trabajador: codigo_trabajador = nup

    clean_nup = nup.replace('-', '').upper()
    clean_ced = cedula.replace('-', '').upper()

    # Verificar existencia previa
    existente = Persona.query.filter(
        (Persona.numero_unico == nup) | (Persona.cedula == cedula) |
        (func.replace(Persona.numero_unico, '-', '') == clean_nup) |
        (func.replace(Persona.cedula, '-', '') == clean_ced)
    ).first()

    if not existente and carnet:
        clean_car = carnet.replace('-', '').upper()
        est_exist = Estudiante.query.filter(
            (Estudiante.carnet_estudiante == carnet) |
            (func.replace(Estudiante.carnet_estudiante, '-', '') == clean_car)
        ).first()
        if est_exist: existente = est_exist.persona

    if not existente and codigo_trabajador:
        clean_cod = codigo_trabajador.replace('-', '').upper()
        trab_exist = Trabajador.query.filter(
            (Trabajador.codigo_trabajador == codigo_trabajador) |
            (func.replace(Trabajador.codigo_trabajador, '-', '') == clean_cod)
        ).first()
        if trab_exist: existente = trab_exist.persona

    if existente:
        persona = existente
    else:
        sede_obj = Sede.query.first()
        sede_id = sede_obj.id if sede_obj else str(uuid.uuid4())

        unidad_obj = UnidadOrganizativa.query.first()
        unidad_id = unidad_obj.id if unidad_obj else str(uuid.uuid4())

        # Validar ciudad de residencia y procedencia
        res_id = ciudad_residencia_id if ciudad_residencia_id and Ciudad.query.get(ciudad_residencia_id) else None
        proc_id = ciudad_procedencia_id if ciudad_procedencia_id and Ciudad.query.get(ciudad_procedencia_id) else None

        if not res_id or not proc_id:
            ciudad_default = Ciudad.query.first()
            if ciudad_default:
                if not res_id: res_id = ciudad_default.id
                if not proc_id: proc_id = ciudad_default.id

        persona = Persona(
            id=str(uuid.uuid4()),
            numero_unico=nup,
            cedula=cedula,
            nombres_apellidos=nombres_apellidos,
            sexo=sexo,
            sede_id=sede_id,
            ciudad_residencia_id=res_id,
            ciudad_procedencia_id=proc_id
        )
        db.session.add(persona)

        if tipo_persona == "Trabajador":
            trabajador = Trabajador(
                persona_id=persona.id,
                codigo_trabajador=codigo_trabajador,
                unidad_organizativa_id=unidad_id,
                cargo=cargo,
                tipo_contrato=tipo_contrato
            )
            db.session.add(trabajador)
        else:
            estudiante = Estudiante(
                persona_id=persona.id,
                carnet_estudiante=carnet,
                area_conocimiento_id=unidad_id,
                carrera=carrera,
                ano_academico=ano_academico,
                grupo=grupo,
                turno=turno
            )
            db.session.add(estudiante)

        db.session.commit()

    # Si se proporcionó evento_id, registrar la asistencia inmediatamente
    msg = f"Persona {persona.nombres_apellidos} registrada exitosamente en el padrón"
    if evento_id:
        actividad = Actividad.query.get(evento_id)
        if actividad:
            if not getattr(actividad, 'asistencia_abierta', True):
                return jsonify({"success": False, "message": "Persona registrada, pero la asistencia para este evento está cerrada"}), 400

            asist_exist = Asistencia.query.filter_by(actividad_id=evento_id, persona_id=persona.id).first()
            if asist_exist:
                return jsonify({"success": True, "message": f"Persona guardada. {persona.nombres_apellidos} ya tenía asistencia en este evento."}), 200

            registrador_id = session.get("user_id")
            if not registrador_id:
                usr = Usuario.query.first()
                if usr: registrador_id = usr.id

            nueva_asist = Asistencia(
                id=str(uuid.uuid4()),
                actividad_id=evento_id,
                persona_id=persona.id,
                usuario_registrador_id=registrador_id,
                timestamp_registro=datetime.now(timezone.utc).isoformat(),
                is_synced=1
            )
            db.session.add(nueva_asist)
            db.session.commit()
            cache.clear()
            msg = f"✅ Persona nueva registrada y asistencia marcada para {persona.nombres_apellidos}"

    return jsonify({
        "success": True,
        "message": msg,
        "persona": {
            "id": persona.id,
            "nombres_apellidos": persona.nombres_apellidos,
            "numero_unico": persona.numero_unico,
            "cedula": persona.cedula,
            "grupo": grupo if persona.estudiante else "N/A",
            "tipo_persona": tipo_persona
        }
    }), 201


# -----------------------------------------------------------------------------
# 6. DELETE /api/asistencia/<asistencia_id> - Eliminación de Marca de Asistencia
# -----------------------------------------------------------------------------

@asistencia_bp.route("/<string:asistencia_id>", methods=["DELETE"])
@login_required
def eliminar_asistencia(asistencia_id: str):
    """
    Elimina un registro de asistencia específico en caso de error humano.
    Limpia el caché para recalcular de inmediato las estadísticas del evento.
    """
    asistencia = Asistencia.query.get(asistencia_id)
    if not asistencia:
        return jsonify({"success": False, "message": "Registro de asistencia no encontrado"}), 404

    actividad_id = asistencia.actividad_id
    nombre_persona = asistencia.persona.nombres_apellidos if asistencia.persona else "Persona"

    db.session.delete(asistencia)
    db.session.commit()
    cache.clear()

    return jsonify({
        "success": True,
        "message": f"Asistencia de {nombre_persona} eliminada correctamente",
        "evento_id": actividad_id
    }), 200