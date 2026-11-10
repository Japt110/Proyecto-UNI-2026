"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - API DE OFERTAS Y APLICACIONES (`/api/pasantias`)
===============================================================================
Endpoints RESTful para el ciclo de vida de convocatorias de pasantías:
- GET  /api/pasantias                      : Listado y filtrado de ofertas disponibles.
- POST /api/pasantias                      : Publicación de nueva oferta de pasantía (Admin/Supervisor).
- GET  /api/pasantias/<id>                 : Detalle completo de una oferta.
- PUT  /api/pasantias/<id>                 : Actualización de estado o información de la oferta.
- DELETE /api/pasantias/<id>               : Eliminación o baja de oferta.
- POST /api/pasantias/<id>/aplicar         : Postulación/aplicación de un estudiante a la pasantía.
- GET  /api/pasantias/mis-aplicaciones     : Historial de postulaciones del estudiante en sesión.
- GET  /api/pasantias/<id>/aplicaciones    : Postulantes recibidos para una oferta (Admin/Supervisor).
- PUT  /api/pasantias/aplicaciones/<id>/estado : Aceptación/rechazo de postulación con transición a Experiencia.
===============================================================================
"""

import os
import uuid
import base64
from datetime import datetime, timezone, date
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, session, current_app, send_from_directory
from sqlalchemy import func
from database import db
from models.ofertas import OfertaPasantia, AplicacionOferta
from models.perfil_estudiante import (
    Estudiante,
    Matricula,
    DireccionEstudiante,
    TelefonoEstudiante,
    EducacionPreviaEstudiante,
)
from models.actores_externos import EntidadReceptora
from models.catalogos import Carrera, Pais, Etnia, Departamento, Municipio, Beca
from models.usuarios_auditoria import Usuario, AuditoriaCambios
from models.experiencias import Experiencia, Pasantia, AsignacionExperiencia, Documento
from core.security import (
    login_required,
    roles_required,
    admin_required,
    student_required,
    company_or_admin_required,
)

pasantias_bp = Blueprint("pasantias_api", __name__)
empresas_bp = Blueprint("empresas_api", __name__)
vinculacion_bp = Blueprint("vinculacion_api", __name__)
estudiantes_bp = Blueprint("estudiantes_api", __name__)


def _log_cambio(tabla: str, operacion: str, registro_id: int, datos_nuevos: dict, datos_anteriores: dict = None):
    """Función auxiliar para registrar DML en AuditoriaCambios."""
    try:
        user_id = session.get("user_id")
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        ua = request.headers.get("User-Agent", "")[:255]

        audit = AuditoriaCambios(
            tabla_afectada=tabla,
            operacion=operacion,
            registro_id=registro_id,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            columnas_modificadas=list(datos_nuevos.keys()) if datos_nuevos else None,
            id_usuario=user_id,
            usuario_bd="sqlite_local",
            ip_origen=ip,
            user_agent=ua,
            transaccion_id=str(uuid.uuid4()),
        )
        db.session.add(audit)
        db.session.commit()
    except Exception:
        db.session.rollback()


# -----------------------------------------------------------------------------
# 1. GET /api/pasantias - Listado con Filtrado Dinámico
# -----------------------------------------------------------------------------

@pasantias_bp.route("", methods=["GET"])
@login_required
def get_pasantias():
    """
    Retorna el catálogo de ofertas de pasantía.
    Soporta filtros de búsqueda por texto, modalidad, sector, ciudad, experiencia y estado.
    """
    search = request.args.get("search", "").strip().lower()
    modalidad = request.args.get("modalidad", "").strip()
    sector = request.args.get("sector", "").strip()
    ciudad = request.args.get("ciudad", "").strip()
    experiencia = request.args.get("experiencia", "").strip()
    estado = request.args.get("estado", "Activo").strip()

    query = OfertaPasantia.query

    if estado and estado.lower() != "todas":
        query = query.filter(OfertaPasantia.estado == estado)

    if modalidad and modalidad.lower() != "todas":
        query = query.filter(OfertaPasantia.modalidad.ilike(f"%{modalidad}%"))

    if sector and sector.lower() != "todos":
        query = query.filter(OfertaPasantia.sector.ilike(f"%{sector}%"))

    if ciudad and ciudad.lower() != "todas":
        query = query.filter(OfertaPasantia.ciudad.ilike(f"%{ciudad}%"))

    if experiencia and experiencia.lower() != "todas":
        query = query.filter(OfertaPasantia.experiencia.ilike(f"%{experiencia}%"))

    ofertas = query.order_by(OfertaPasantia.id_oferta.desc()).all()

    # Filtro de búsqueda libre en título o descripción
    if search:
        ofertas = [
            o for o in ofertas
            if search in o.titulo.lower() or search in o.descripcion.lower() or search in o.sector.lower() or search in o.ciudad.lower()
        ]

    return jsonify({
        "success": True,
        "total": len(ofertas),
        "pasantias": [o.to_dict() for o in ofertas]
    }), 200


# -----------------------------------------------------------------------------
# 2. POST /api/pasantias - Publicación de Nueva Oferta (Posteo)
# -----------------------------------------------------------------------------

@pasantias_bp.route("", methods=["POST"])
@company_or_admin_required
def create_pasantia():
    """
    Publica una nueva oferta de pasantía en la plataforma.
    Acepta parámetros del formulario y registra la auditoría forense.
    """
    data = request.get_json() or {}
    titulo = data.get("titulo", "").strip()
    descripcion = data.get("descripcion", "").strip()

    if not titulo or not descripcion:
        return jsonify({"success": False, "message": "Título y descripción son campos obligatorios"}), 400

    tipo = data.get("tipo", "Académica")
    modalidad = data.get("modalidad", "Presencial")
    duracion = data.get("duracion", "160H")
    
    # Extraer horas numéricas si vienen formateadas como '160H'
    try:
        duracion_horas = int("".join([c for c in duracion if c.isdigit()])) or 160
    except Exception:
        duracion_horas = 160

    experiencia = data.get("experiencia", "Sin experiencia")
    sector = data.get("sector", "Tecnología")
    ciudad = data.get("ciudad", "Managua")
    requisitos = data.get("requisitos")
    cupos = int(data.get("cupos", 1))
    id_entidad = data.get("id_entidad")
    id_carrera = data.get("id_carrera")

    nueva_oferta = OfertaPasantia(
        titulo=titulo,
        tipo=tipo,
        modalidad=modalidad,
        duracion=duracion,
        duracion_horas=duracion_horas,
        experiencia=experiencia,
        sector=sector,
        ciudad=ciudad,
        descripcion=descripcion,
        requisitos=requisitos,
        cupos=cupos,
        estado="Activo",
        id_entidad=id_entidad,
        id_carrera=id_carrera,
        id_usuario_creador=session.get("user_id"),
    )

    db.session.add(nueva_oferta)
    db.session.commit()

    _log_cambio(
        tabla="ofertas_pasantia",
        operacion="INSERT",
        registro_id=nueva_oferta.id_oferta,
        datos_nuevos=nueva_oferta.to_dict(),
    )

    return jsonify({
        "success": True,
        "message": "Oferta de pasantía publicada exitosamente",
        "pasantia": nueva_oferta.to_dict(),
    }), 201


# -----------------------------------------------------------------------------
# 3. GET /api/pasantias/<id> - Detalle de Oferta
# -----------------------------------------------------------------------------

@pasantias_bp.route("/<int:id_oferta>", methods=["GET"])
@login_required
def get_pasantia_detalle(id_oferta):
    """Retorna la información completa de una pasantía específica."""
    oferta = OfertaPasantia.query.get(id_oferta)
    if not oferta:
        return jsonify({"success": False, "message": "Oferta no encontrada"}), 404

    return jsonify({"success": True, "pasantia": oferta.to_dict()}), 200


# -----------------------------------------------------------------------------
# 4. PUT /api/pasantias/<id> - Actualización de Oferta
# -----------------------------------------------------------------------------

@pasantias_bp.route("/<int:id_oferta>", methods=["PUT"])
@company_or_admin_required
def update_pasantia(id_oferta):
    """Actualiza los datos o estado de una oferta (Empresas y Administradores)."""
    oferta = OfertaPasantia.query.get(id_oferta)
    if not oferta:
        return jsonify({"success": False, "message": "Oferta no encontrada"}), 404

    datos_previos = oferta.to_dict()
    data = request.get_json() or {}

    for campo in ["titulo", "tipo", "modalidad", "duracion", "experiencia", "sector", "ciudad", "descripcion", "requisitos", "estado", "cupos"]:
        if campo in data:
            setattr(oferta, campo, data[campo])

    db.session.commit()
    _log_cambio("ofertas_pasantia", "UPDATE", oferta.id_oferta, oferta.to_dict(), datos_previos)

    return jsonify({"success": True, "message": "Oferta actualizada exitosamente", "pasantia": oferta.to_dict()}), 200


# -----------------------------------------------------------------------------
# 4.1 DELETE /api/pasantias/<id> - Eliminación de Oferta
# -----------------------------------------------------------------------------

@pasantias_bp.route("/<int:id_oferta>", methods=["DELETE"])
@company_or_admin_required
def delete_pasantia(id_oferta):
    """Elimina o cancela una oferta de pasantía (Empresas y Administradores)."""
    oferta = OfertaPasantia.query.get(id_oferta)
    if not oferta:
        return jsonify({"success": False, "message": "Oferta no encontrada"}), 404

    datos_previos = oferta.to_dict()
    # Eliminar postulaciones asociadas si existen
    AplicacionOferta.query.filter_by(id_oferta=id_oferta).delete()
    db.session.delete(oferta)
    db.session.commit()

    _log_cambio("ofertas_pasantia", "DELETE", id_oferta, None, datos_previos)
    return jsonify({"success": True, "message": "Oferta eliminada exitosamente del sistema"}), 200


# -----------------------------------------------------------------------------
# 5. POST /api/pasantias/<id>/aplicar - Sistema de Aplicación / Postulación (Estudiantes)
# -----------------------------------------------------------------------------

@pasantias_bp.route("/<int:id_oferta>/aplicar", methods=["POST"])
@student_required
def aplicar_a_pasantia(id_oferta):
    """
    Registra la postulación de un estudiante a una oferta de pasantía.
    Exclusivo para Estudiantes (@student_required). Administradores no pueden postularse.
    Valida elegibilidad académica estricta (CU-01, CU-03, CU-09):
    - Matrícula vigente/activa.
    - Avance académico restringido a 4to o 5to año de carrera.
    - Empresa anfitriona aprobada por la universidad (CU-08).
    - Previene postulaciones duplicadas.
    """
    oferta = OfertaPasantia.query.get(id_oferta)
    if not oferta:
        return jsonify({"success": False, "message": "La oferta de pasantía no existe"}), 404

    data = request.get_json(silent=True) or {}

    if oferta.estado != "Activo":
        return jsonify({"success": False, "message": "Esta oferta ya no se encuentra activa para postulaciones"}), 400

    # Parámetros modulares de elegibilidad desde configuración (.env)
    min_year = current_app.config.get("ACADEMIC_MIN_YEAR", 4)
    max_year = current_app.config.get("ACADEMIC_MAX_YEAR", 5)
    allowed_years = list(range(min_year, max_year + 1))
    require_company_approval = current_app.config.get("COMPANY_REQUIRE_APPROVAL", True)

    # Validar aprobación institucional de la empresa si está configurado como requerido
    if require_company_approval and oferta.entidad and getattr(oferta.entidad, "estado_aprobacion", None) == "Pendiente_Aprobacion":
        return jsonify({
            "success": False,
            "message": f"La empresa '{oferta.entidad.nombre}' se encuentra pendiente de validación institucional (CU-08)."
        }), 403

    # Determinar el estudiante solicitante directamente desde la sesión autenticada
    user_id = session.get("user_id")
    user = Usuario.query.get(user_id) if user_id else None
    id_estudiante = user.id_estudiante if user else None

    if not id_estudiante:
        return jsonify({
            "success": False,
            "message": "Acceso denegado: No se encontró un perfil de estudiante vinculado a su cuenta (CU-01)."
        }), 403

    # =========================================================================
    # REGLAS DE NEGOCIO: AUDITORÍA DE ELEGIBILIDAD ACADÉMICA (CU-01, CU-09)
    # =========================================================================
    matricula = Matricula.query.filter_by(
        id_estudiante=id_estudiante,
        estado="Activa"
    ).order_by(Matricula.anio_academico.desc()).first()

    if not matricula:
        return jsonify({
            "success": False,
            "message": "Elegibilidad no cumplida: El estudiante no cuenta con una matrícula activa registrada (CU-01 / CU-09)."
        }), 403

    if matricula.anio_academico not in allowed_years:
        return jsonify({
            "success": False,
            "message": f"Elegibilidad no cumplida: El estudiante se encuentra en {matricula.anio_academico}º año. Las pasantías están restringidas exclusivamente a estudiantes de {min_year}to o {max_year}to año (CU-06 / CU-09)."
        }), 403

    # Verificar si ya existe postulación previa
    existente = AplicacionOferta.query.filter_by(
        id_oferta=id_oferta,
        id_estudiante=id_estudiante,
    ).first()

    if existente:
        return jsonify({
            "success": False,
            "message": f"Ya has enviado una postulación a esta pasantía (Estado: {existente.estado})",
            "aplicacion": existente.to_dict()
        }), 409

    mensaje = data.get("mensaje", "Solicitud formal de pasantía vinculando expediente socio-académico.")

    # Documentos autorizados por el estudiante para esta postulación
    docs_compartidos = data.get("documentos_compartidos")
    docs_compartidos_str = None
    if docs_compartidos is not None:
        import json
        if isinstance(docs_compartidos, list):
            docs_compartidos_str = json.dumps([int(x) for x in docs_compartidos if str(x).isdigit()])
        elif isinstance(docs_compartidos, str):
            docs_compartidos_str = docs_compartidos

    nueva_aplicacion = AplicacionOferta(
        id_oferta=id_oferta,
        id_estudiante=id_estudiante,
        fecha_postulacion=datetime.now(timezone.utc),
        estado="Postulado",
        mensaje=mensaje,
        documentos_compartidos=docs_compartidos_str,
    )

    db.session.add(nueva_aplicacion)
    db.session.commit()

    _log_cambio(
        tabla="aplicaciones_oferta",
        operacion="INSERT",
        registro_id=nueva_aplicacion.id_aplicacion,
        datos_nuevos=nueva_aplicacion.to_dict(),
    )

    return jsonify({
        "success": True,
        "message": f"¡Solicitud enviada con éxito para {oferta.titulo}!",
        "aplicacion": nueva_aplicacion.to_dict(),
    }), 201


# -----------------------------------------------------------------------------
# 6. GET /api/pasantias/mis-aplicaciones - Historial de Aplicaciones del Estudiante
# -----------------------------------------------------------------------------

@pasantias_bp.route("/mis-aplicaciones", methods=["GET"])
@student_required
def get_mis_aplicaciones():
    """Retorna las solicitudes enviadas por el estudiante autenticado (CU-04). Exclusivo de Estudiantes."""
    user_id = session.get("user_id")
    user = Usuario.query.get(user_id) if user_id else None
    id_estudiante = user.id_estudiante if user else None

    if not id_estudiante:
        return jsonify({"success": True, "total": 0, "aplicaciones": []}), 200

    apps = AplicacionOferta.query.filter_by(id_estudiante=id_estudiante).order_by(
        AplicacionOferta.id_aplicacion.desc()
    ).all()

    return jsonify({
        "success": True,
        "total": len(apps),
        "aplicaciones": [a.to_dict() for a in apps]
    }), 200


# -----------------------------------------------------------------------------
# 6.1 GET /api/estudiantes/perfil - Ficha Socio-Académica del Estudiante (CU-01)
# -----------------------------------------------------------------------------

@pasantias_bp.route("/perfil", methods=["GET"])
@pasantias_bp.route("/estudiantes/perfil", methods=["GET"])
@estudiantes_bp.route("/perfil", methods=["GET"])
@login_required
def get_perfil_estudiante():
    """Retorna la ficha socio-académica completa del estudiante autenticado desde SQLAlchemy."""
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id) if user_id else None
    if not usuario:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    estudiante = Estudiante.query.get(usuario.id_estudiante) if usuario.id_estudiante else None

    if not estudiante:
        return jsonify({
            "success": True,
            "es_estudiante": False,
            "usuario": {
                "id": usuario.id_usuario,
                "username": usuario.nombre_usuario,
                "email": usuario.email,
                "rol": usuario.rol,
            }
        }), 200

    matricula_activa = Matricula.query.filter_by(
        id_estudiante=estudiante.id_estudiante,
        estado="Activa"
    ).order_by(Matricula.id_matricula.desc()).first()

    carrera_nombre = matricula_activa.carrera.nombre if matricula_activa and matricula_activa.carrera else "Ingeniería de Sistemas"
    anio_academico = matricula_activa.anio_academico if matricula_activa else 4

    telefonos = [{
        "id_telefono": t.id_telefono,
        "numero": t.numero,
        "tipo": t.tipo,
        "es_principal": t.es_principal,
    } for t in estudiante.telefonos]

    direcciones = [{
        "id_direccion": d.id_direccion,
        "direccion": d.direccion_domiciliar,
        "zona": d.zona,
        "comunidad": d.comunidad or "",
        "municipio": d.municipio.nombre if d.municipio else "",
        "departamento": d.municipio.departamento.nombre if d.municipio and d.municipio.departamento else "",
        "es_principal": d.es_principal,
    } for d in estudiante.direcciones]

    educacion = [{
        "id_educacion": ed.id_educacion,
        "titulo": ed.titulo_obtenido,
        "anio": ed.anio_graduacion,
        "centro": ed.centro_educativo.nombre if ed.centro_educativo else "",
    } for ed in estudiante.educaciones_previas]

    return jsonify({
        "success": True,
        "es_estudiante": True,
        "perfil": {
            "id_estudiante": estudiante.id_estudiante,
            "cup": estudiante.cup,
            "cedula": estudiante.cedula,
            "nombre": estudiante.nombre,
            "apellido": estudiante.apellido,
            "nombre_completo": f"{estudiante.nombre} {estudiante.apellido}",
            "email": usuario.email,
            "fecha_nacimiento": estudiante.fecha_nacimiento.strftime("%Y-%m-%d") if estudiante.fecha_nacimiento else "",
            "edad": estudiante.edad or estudiante.calcular_edad(),
            "sexo": estudiante.sexo,
            "estado_civil": estudiante.estado_civil or "Soltero(a)",
            "hijos": estudiante.hijos,
            "pais": estudiante.pais_origen.nombre if estudiante.pais_origen else "Nicaragua",
            "etnia": estudiante.etnia.nombre if estudiante.etnia else "Mestizo",
            "carrera": carrera_nombre,
            "anio_academico": anio_academico,
            "matricula_estado": matricula_activa.estado if matricula_activa else "Activa",
            "matricula_periodo": matricula_activa.periodo_academico if matricula_activa else "I Semestre 2026",
            "beca": matricula_activa.beca.nombre if matricula_activa and matricula_activa.beca else "Sin Beca",
            "telefonos": telefonos,
            "telefono_principal": telefonos[0]["numero"] if telefonos else "",
            "direcciones": direcciones,
            "direccion_principal": direcciones[0]["direccion"] if direcciones else "",
            "departamento_principal": direcciones[0]["departamento"] if direcciones else "Managua",
            "municipio_principal": direcciones[0]["municipio"] if direcciones else "Managua",
            "educacion_previa": educacion,
            "documentos": [doc.to_dict() for doc in estudiante.documentos],
        }
    }), 200


# -----------------------------------------------------------------------------
# 6.2 PUT /api/estudiantes/perfil - Actualización de Perfil (CU-01)
# -----------------------------------------------------------------------------

@pasantias_bp.route("/perfil", methods=["PUT"])
@pasantias_bp.route("/estudiantes/perfil", methods=["PUT"])
@estudiantes_bp.route("/perfil", methods=["PUT"])
@login_required
def update_perfil_estudiante():
    """Actualiza los datos socio-demográficos y de contacto del estudiante en SQLAlchemy."""
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id) if user_id else None
    if not usuario:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    data = request.get_json() or {}
    estudiante = Estudiante.query.get(usuario.id_estudiante) if usuario.id_estudiante else None

    if not estudiante:
        if "email" in data and data["email"]:
            usuario.email = data["email"].strip().lower()
        if "has_2fa" in data:
            usuario.has_2fa = bool(data["has_2fa"])
        db.session.commit()
        return jsonify({"success": True, "message": "Perfil de usuario actualizado", "has_2fa": usuario.has_2fa}), 200

    if "has_2fa" in data:
        usuario.has_2fa = bool(data["has_2fa"])
    if "nombre" in data and data["nombre"]:
        estudiante.nombre = data["nombre"].strip()
    if "apellido" in data and data["apellido"]:
        estudiante.apellido = data["apellido"].strip()
    if "estado_civil" in data:
        estudiante.estado_civil = data["estado_civil"]
    if "hijos" in data and str(data["hijos"]).isdigit():
        estudiante.hijos = int(data["hijos"])
    if "email" in data and data["email"]:
        usuario.email = data["email"].strip().lower()

    telefono_num = data.get("telefono") or data.get("telefono_principal")
    if telefono_num:
        tel = TelefonoEstudiante.query.filter_by(id_estudiante=estudiante.id_estudiante, es_principal=True).first()
        if tel:
            tel.numero = str(telefono_num).strip()
        else:
            nuevo_tel = TelefonoEstudiante(
                id_estudiante=estudiante.id_estudiante,
                numero=str(telefono_num).strip(),
                tipo="Móvil",
                es_principal=True,
            )
            db.session.add(nuevo_tel)

    dir_texto = data.get("direccion") or data.get("direccion_principal")
    if dir_texto:
        dir_obj = DireccionEstudiante.query.filter_by(id_estudiante=estudiante.id_estudiante, es_principal=True).first()
        if dir_obj:
            dir_obj.direccion_domiciliar = str(dir_texto).strip()
        else:
            mun = Municipio.query.first()
            nueva_dir = DireccionEstudiante(
                id_estudiante=estudiante.id_estudiante,
                id_municipio=mun.id_municipio if mun else 1,
                direccion_domiciliar=str(dir_texto).strip(),
                zona="Urbano",
                es_principal=True,
            )
            db.session.add(nueva_dir)

    db.session.commit()
    _log_cambio("estudiantes", "UPDATE", estudiante.id_estudiante, {"nombre": estudiante.nombre, "apellido": estudiante.apellido})

    return jsonify({
        "success": True,
        "message": "Ficha socio-académica y perfil actualizados exitosamente en la base de datos.",
        "nombre_completo": f"{estudiante.nombre} {estudiante.apellido}",
    }), 200


# -----------------------------------------------------------------------------
# 6.3 POST /api/estudiantes/documentos - Carga y Registro de Documentos (CV, Récord, Licencia, etc.)
# -----------------------------------------------------------------------------

@pasantias_bp.route("/estudiantes/documentos", methods=["POST"])
@pasantias_bp.route("/documentos", methods=["POST"])
@estudiantes_bp.route("/documentos", methods=["POST"])
@student_required
def subir_documento_estudiante():
    """
    Permite al estudiante subir documentos personales (CV, Récord Policial,
    Licencia de Conducir, Cédula, etc.) persistidos directamente en la tabla 'documentos'.
    """
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id) if user_id else None
    if not usuario or not usuario.id_estudiante:
        return jsonify({
            "success": False,
            "message": "Acceso denegado: Solo estudiantes pueden subir documentos a su expediente."
        }), 403

    estudiante = Estudiante.query.get(usuario.id_estudiante)
    if not estudiante:
        return jsonify({"success": False, "message": "Ficha de estudiante no encontrada"}), 404

    tipo_documento = (
        request.form.get("tipo_documento")
        or request.form.get("tipo")
        or (request.get_json(silent=True) or {}).get("tipo_documento")
        or "CV"
    ).strip()

    upload_dir = os.path.join(current_app.root_path, "static", "uploads", "documentos")
    os.makedirs(upload_dir, exist_ok=True)

    original_filename = "documento.pdf"
    file_bytes = None
    mime_type = "application/pdf"

    if "archivo" in request.files or "file" in request.files or "documento" in request.files:
        f = request.files.get("archivo") or request.files.get("file") or request.files.get("documento")
        if f and f.filename:
            original_filename = secure_filename(f.filename)
            file_bytes = f.read()
            mime_type = f.content_type or "application/octet-stream"

    if not file_bytes and request.is_json:
        data = request.get_json() or {}
        b64 = data.get("contenido_base64") or data.get("base64")
        if b64:
            if "," in b64:
                b64 = b64.split(",", 1)[1]
            try:
                file_bytes = base64.b64decode(b64)
                original_filename = secure_filename(data.get("nombre_archivo") or "documento.pdf")
                mime_type = data.get("mime_type") or "application/pdf"
            except Exception:
                return jsonify({"success": False, "message": "Contenido base64 inválido"}), 400

    if not file_bytes:
        return jsonify({
            "success": False,
            "message": "Debe adjuntar un archivo válido (PDF, Word, Imagen) o enviar base64."
        }), 400

    safe_name = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, "wb") as out:
        out.write(file_bytes)

    ruta_publica = f"/static/uploads/documentos/{safe_name}"

    nuevo_doc = Documento(
        id_estudiante=estudiante.id_estudiante,
        tipo_documento=tipo_documento,
        nombre_original=original_filename,
        ruta_archivo=ruta_publica,
        tamano_bytes=len(file_bytes),
        mime_type=mime_type,
        fecha_subida=datetime.now(timezone.utc),
        estado="Vigente",
    )

    db.session.add(nuevo_doc)
    db.session.commit()
    _log_cambio("documentos", "INSERT", nuevo_doc.id_documento, nuevo_doc.to_dict())

    return jsonify({
        "success": True,
        "message": f"Documento '{original_filename}' ({tipo_documento}) subido y registrado exitosamente en la base de datos.",
        "documento": nuevo_doc.to_dict(),
    }), 201


# -----------------------------------------------------------------------------
# 6.4 GET /api/estudiantes/documentos - Listado de Documentos del Estudiante
# -----------------------------------------------------------------------------

@pasantias_bp.route("/estudiantes/documentos", methods=["GET"])
@pasantias_bp.route("/documentos", methods=["GET"])
@estudiantes_bp.route("/documentos", methods=["GET"])
@login_required
def get_documentos_estudiante():
    """Retorna todos los documentos asociados al estudiante autenticado."""
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id) if user_id else None
    if not usuario or not usuario.id_estudiante:
        return jsonify({"success": True, "total": 0, "documentos": []}), 200

    docs = Documento.query.filter_by(id_estudiante=usuario.id_estudiante).order_by(Documento.id_documento.desc()).all()
    return jsonify({
        "success": True,
        "total": len(docs),
        "documentos": [d.to_dict() for d in docs]
    }), 200


# -----------------------------------------------------------------------------
# 6.5 DELETE /api/estudiantes/documentos/<id> - Eliminación de Documento
# -----------------------------------------------------------------------------

@pasantias_bp.route("/estudiantes/documentos/<int:id_documento>", methods=["DELETE"])
@pasantias_bp.route("/documentos/<int:id_documento>", methods=["DELETE"])
@estudiantes_bp.route("/documentos/<int:id_documento>", methods=["DELETE"])
@login_required
def delete_documento_estudiante(id_documento):
    """Elimina un documento de la base de datos y de almacenamiento físico."""
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id) if user_id else None
    if not usuario:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    doc = Documento.query.get(id_documento)
    if not doc:
        return jsonify({"success": False, "message": "Documento no encontrado"}), 404

    if usuario.rol != "Administrador" and doc.id_estudiante != usuario.id_estudiante:
        return jsonify({"success": False, "message": "Acceso denegado: No puede eliminar este documento."}), 403

    datos_previos = doc.to_dict()

    if doc.ruta_archivo and doc.ruta_archivo.startswith("/static/"):
        rel_path = doc.ruta_archivo.lstrip("/")
        abs_path = os.path.join(current_app.root_path, rel_path)
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
            except Exception:
                pass

    db.session.delete(doc)
    db.session.commit()
    _log_cambio("documentos", "DELETE", id_documento, None, datos_previos)

    return jsonify({"success": True, "message": "Documento eliminado exitosamente de la base de datos."}), 200


# -----------------------------------------------------------------------------
# 7. GET /api/pasantias/<id>/aplicaciones - Lista de Postulantes con Expediente y Documentos (CU-07)
# -----------------------------------------------------------------------------

@pasantias_bp.route("/<int:id_oferta>/aplicaciones", methods=["GET"])
@company_or_admin_required
def get_postulantes_oferta(id_oferta):
    """
    Retorna los estudiantes postulantes a una oferta para evaluación empresarial (CU-07).
    Incluye la ficha socio-académica completa del estudiante y todos los documentos vinculados
    (CV, Récord Policial, Licencia de Conducir, etc.) para que el ofertante pueda ejercer su veredicto.
    """
    oferta = OfertaPasantia.query.get(id_oferta)
    if not oferta:
        return jsonify({"success": False, "message": "Oferta no encontrada"}), 404

    apps = AplicacionOferta.query.filter_by(id_oferta=id_oferta).order_by(AplicacionOferta.id_aplicacion.desc()).all()
    resultado = []

    for app in apps:
        app_dict = app.to_dict()
        est = app.estudiante
        if est:
            matricula_activa = Matricula.query.filter_by(
                id_estudiante=est.id_estudiante,
                estado="Activa"
            ).order_by(Matricula.id_matricula.desc()).first()

            # Documentos autorizados por el estudiante para esta postulación
            todos_docs = [doc.to_dict() for doc in est.documentos]
            if app.documentos_compartidos:
                try:
                    import json
                    allowed_ids = set(json.loads(app.documentos_compartidos))
                    docs_autorizados = [d for d in todos_docs if d["id_documento"] in allowed_ids]
                except Exception:
                    docs_autorizados = todos_docs
            else:
                docs_autorizados = todos_docs

            candidato_info = {
                "id_estudiante": est.id_estudiante,
                "nombre": est.nombre,
                "apellido": est.apellido,
                "nombre_completo": f"{est.nombre} {est.apellido}",
                "cup": est.cup,
                "cedula": est.cedula,
                "email": est.usuario.email if est.usuario else None,
                "edad": est.edad or est.calcular_edad(),
                "sexo": est.sexo,
                "carrera": matricula_activa.carrera.nombre if matricula_activa and matricula_activa.carrera else "Carrera Afín",
                "anio_academico": matricula_activa.anio_academico if matricula_activa else 4,
                "matricula_estado": matricula_activa.estado if matricula_activa else "Activa",
                "matricula_periodo": matricula_activa.periodo_academico if matricula_activa else "I Semestre 2026",
                "beca": matricula_activa.beca.nombre if matricula_activa and matricula_activa.beca else "Sin Beca",
                "telefonos": [t.numero for t in est.telefonos],
                "telefono_principal": est.telefonos[0].numero if est.telefonos else "N/A",
                "direcciones": [d.direccion_domiciliar for d in est.direcciones],
                "direccion_principal": est.direcciones[0].direccion_domiciliar if est.direcciones else "N/A",
                "documentos": docs_autorizados,
                "total_documentos": len(docs_autorizados),
                "tiene_documentos_restringidos": len(docs_autorizados) < len(todos_docs),
            }
            app_dict["candidato"] = candidato_info
            app_dict["documentos"] = docs_autorizados
        else:
            app_dict["candidato"] = None
            app_dict["documentos"] = []

        resultado.append(app_dict)

    return jsonify({
        "success": True,
        "oferta_titulo": oferta.titulo,
        "total_postulantes": len(resultado),
        "postulaciones": resultado,
        "aplicaciones": resultado,
    }), 200


# -----------------------------------------------------------------------------
# 8. PUT /api/pasantias/aplicaciones/<id>/estado - Evaluación y Selección (CU-04, CU-07)
# -----------------------------------------------------------------------------

@pasantias_bp.route("/aplicaciones/<int:id_aplicacion>/estado", methods=["PUT"])
@company_or_admin_required
def cambiar_estado_aplicacion(id_aplicacion):
    """
    Actualiza el estado de una postulación (CU-04 / CU-07):
    Estados permitidos: 'Postulado', 'En revision', 'Entrevista programada', 'Aceptado', 'Rechazado'.
    Si se aprueba ('Aceptado' o 'Aceptada'), se genera atómicamente la Experiencia formativa
    en el Subdominio D (Experiencia + Pasantia + AsignacionExperiencia).
    """
    aplicacion = AplicacionOferta.query.get(id_aplicacion)
    if not aplicacion:
        return jsonify({"success": False, "message": "Postulación no encontrada"}), 404

    data = request.get_json() or {}
    nuevo_estado = data.get("estado") or data.get("nuevo_estado")

    estados_validos = [
        "Postulado",
        "En revision",
        "Entrevista programada",
        "Aceptado",
        "Aceptada",
        "Rechazado",
        "Rechazada",
        "Pendiente",
    ]
    if nuevo_estado not in estados_validos:
        return jsonify({
            "success": False,
            "message": f"Estado '{nuevo_estado}' no válido. Opciones: Postulado, En revision, Entrevista programada, Aceptado, Rechazado."
        }), 400

    datos_previos = aplicacion.to_dict()
    aplicacion.estado = nuevo_estado

    id_experiencia = None
    # Si fue aceptada y no tenía experiencia previa, crear la Experiencia formal
    if nuevo_estado in ("Aceptado", "Aceptada") and not aplicacion.id_experiencia_generada:
        oferta = aplicacion.oferta
        hoy = date.today()
        fin_estimado = hoy.replace(month=min(hoy.month + 4, 12)) if hoy.month <= 8 else hoy.replace(year=hoy.year + 1, month=1)

        exp = Experiencia(
            id_estudiante=aplicacion.id_estudiante,
            tipo_experiencia="Pasantia",
            modalidad=oferta.modalidad if oferta else "Presencial",
            fecha_inicio=hoy,
            fecha_fin=fin_estimado,
            horas_totales=oferta.duracion_horas if oferta else 160,
            estado="En_Proceso",
            origen="Convocatoria_Institucional",
        )
        db.session.add(exp)
        db.session.flush()

        pas = Pasantia(id_experiencia=exp.id_experiencia, tipo=oferta.tipo if oferta else "Laboral")
        db.session.add(pas)

        # Si la oferta tiene entidad asignada, registrar la asignación inicial
        if oferta and oferta.id_entidad:
            asig = AsignacionExperiencia(
                id_experiencia=exp.id_experiencia,
                rol="Supervisor",
                id_tutor=None,
                id_supervisor=None,
                id_entidad=oferta.id_entidad,
                fecha_desde=hoy,
                activa=True,
            )
            db.session.add(asig)

        aplicacion.id_experiencia_generada = exp.id_experiencia
        id_experiencia = exp.id_experiencia

    db.session.commit()
    _log_cambio("aplicaciones_oferta", "UPDATE", aplicacion.id_aplicacion, aplicacion.to_dict(), datos_previos)

    return jsonify({
        "success": True,
        "message": f"Postulación actualizada a estado '{nuevo_estado}'",
        "aplicacion": aplicacion.to_dict(),
        "id_experiencia_generada": id_experiencia,
    }), 200


# -----------------------------------------------------------------------------
# 9. ENDPOINTS DE GESTIÓN DE EMPRESAS (CU-05, CU-08)
# -----------------------------------------------------------------------------

@empresas_bp.route("", methods=["GET"])
@pasantias_bp.route("/empresas", methods=["GET"])
@login_required
def get_empresas():
    """Retorna el listado de empresas con su estado de validación institucional."""
    estado = request.args.get("estado")
    query = EntidadReceptora.query
    if estado:
        query = query.filter_by(estado_aprobacion=estado)
    empresas = query.order_by(EntidadReceptora.id_entidad.desc()).all()
    return jsonify({
        "success": True,
        "total": len(empresas),
        "empresas": [e.to_dict() for e in empresas]
    }), 200


@empresas_bp.route("", methods=["POST"])
@pasantias_bp.route("/empresas", methods=["POST"])
@company_or_admin_required
def registrar_empresa():
    """Registra una nueva entidad receptora con estado inicial 'Pendiente_Aprobacion' (CU-05)."""
    data = request.get_json() or {}
    nombre = data.get("nombre", "").strip()
    tipo = data.get("tipo", "Privada").strip()

    if not nombre:
        return jsonify({"success": False, "message": "El nombre de la empresa es obligatorio"}), 400

    empresa = EntidadReceptora(
        nombre=nombre,
        tipo=tipo,
        contacto_nombre=data.get("contacto_nombre"),
        contacto_email=data.get("contacto_email"),
        contacto_telefono=data.get("contacto_telefono"),
        estado_aprobacion="Pendiente_Aprobacion",
    )
    db.session.add(empresa)
    db.session.commit()

    _log_cambio("entidades_receptoras", "INSERT", empresa.id_entidad, empresa.to_dict())

    return jsonify({
        "success": True,
        "message": "Empresa registrada exitosamente. Pendiente de validación institucional (CU-05, CU-08).",
        "empresa": empresa.to_dict(),
    }), 201


@empresas_bp.route("/<int:id_entidad>/aprobar", methods=["PUT"])
@pasantias_bp.route("/empresas/<int:id_entidad>/aprobar", methods=["PUT"])
@admin_required
def aprobar_empresa(id_entidad):
    """El Administrador Universitario valida y aprueba una entidad receptora (CU-08). Exclusivo de Administradores."""
    empresa = EntidadReceptora.query.get(id_entidad)
    if not empresa:
        return jsonify({"success": False, "message": "Empresa no encontrada"}), 404

    datos_previos = empresa.to_dict()
    empresa.estado_aprobacion = "Aprobada"
    db.session.commit()

    _log_cambio("entidades_receptoras", "UPDATE", empresa.id_entidad, empresa.to_dict(), datos_previos)

    return jsonify({
        "success": True,
        "message": f"Empresa '{empresa.nombre}' aprobada formalmente para recibir pasantes.",
        "empresa": empresa.to_dict(),
    }), 200


@empresas_bp.route("/<int:id_entidad>/rechazar", methods=["PUT"])
@pasantias_bp.route("/empresas/<int:id_entidad>/rechazar", methods=["PUT"])
@admin_required
def rechazar_empresa(id_entidad):
    """El Administrador Universitario rechaza una entidad receptora por inconsistencias (CU-08). Exclusivo de Administradores."""
    empresa = EntidadReceptora.query.get(id_entidad)
    if not empresa:
        return jsonify({"success": False, "message": "Empresa no encontrada"}), 404

    datos_previos = empresa.to_dict()
    empresa.estado_aprobacion = "Rechazada"
    db.session.commit()

    _log_cambio("entidades_receptoras", "UPDATE", empresa.id_entidad, empresa.to_dict(), datos_previos)

    return jsonify({
        "success": True,
        "message": f"Empresa '{empresa.nombre}' rechazada institucionalmente.",
        "empresa": empresa.to_dict(),
    }), 200


# -----------------------------------------------------------------------------
# 10. ENDPOINT DE REPORTES Y MÉTRICAS DE VINCULACIÓN (CU-10)
# -----------------------------------------------------------------------------

@vinculacion_bp.route("/metricas", methods=["GET"])
@pasantias_bp.route("/vinculacion/metricas", methods=["GET"])
@admin_required
def get_metricas_vinculacion():
    """
    Genera reportes estadísticos y métricas de vinculación institucional (CU-10):
    - Demanda de pasantías por carrera.
    - Absorción de talento universitario por empresa.
    - Tasa de efectividad del matching y desglose de postulaciones.
    """
    total_ofertas = OfertaPasantia.query.count()
    ofertas_activas = OfertaPasantia.query.filter_by(estado="Activo").count()
    total_postulaciones = AplicacionOferta.query.count()
    postulaciones_aceptadas = AplicacionOferta.query.filter(
        AplicacionOferta.estado.in_(("Aceptado", "Aceptada"))
    ).count()

    # Demanda por carrera (ofertas asociadas a carreras)
    carreras = Carrera.query.all()
    demanda_por_carrera = []
    for c in carreras:
        ofertas_carrera = OfertaPasantia.query.filter_by(id_carrera=c.id_carrera).count()
        # Postulaciones de estudiantes en esta carrera
        postulaciones_carrera = (
            db.session.query(func.count(AplicacionOferta.id_aplicacion))
            .join(Matricula, Matricula.id_estudiante == AplicacionOferta.id_estudiante)
            .filter(Matricula.id_carrera == c.id_carrera, Matricula.estado == "Activa")
            .scalar() or 0
        )
        if ofertas_carrera > 0 or postulaciones_carrera > 0:
            demanda_por_carrera.append({
                "id_carrera": c.id_carrera,
                "carrera": c.nombre,
                "ofertas_disponibles": ofertas_carrera,
                "postulaciones_recibidas": postulaciones_carrera,
            })

    # Absorción de talento por empresa (pasantías generadas/aceptadas)
    empresas = EntidadReceptora.query.all()
    absorcion_por_empresa = []
    for e in empresas:
        # Contar ofertas de esta empresa
        ofertas_ids = [o.id_oferta for o in OfertaPasantia.query.filter_by(id_entidad=e.id_entidad).all()]
        total_pasantias_empresa = len(ofertas_ids)
        talento_absorbido = 0
        if ofertas_ids:
            talento_absorbido = AplicacionOferta.query.filter(
                AplicacionOferta.id_oferta.in_(ofertas_ids),
                AplicacionOferta.estado.in_(("Aceptado", "Aceptada")),
            ).count()

        absorcion_por_empresa.append({
            "id_entidad": e.id_entidad,
            "empresa": e.nombre,
            "estado_aprobacion": e.estado_aprobacion or "Aprobada",
            "ofertas_publicadas": total_pasantias_empresa,
            "talento_absorbido": talento_absorbido,
        })

    # Ordenar por absorción de talento descendente
    absorcion_por_empresa.sort(key=lambda x: x["talento_absorbido"], reverse=True)

    tasa_conversion = (
        round((postulaciones_aceptadas / total_postulaciones * 100), 2)
        if total_postulaciones > 0 else 0.0
    )

    return jsonify({
        "success": True,
        "metricas": {
            "resumen_general": {
                "total_ofertas": total_ofertas,
                "ofertas_activas": ofertas_activas,
                "total_postulaciones": total_postulaciones,
                "postulaciones_aceptadas": postulaciones_aceptadas,
                "tasa_efectividad_matching_porcentaje": tasa_conversion,
            },
            "demanda_por_carrera": demanda_por_carrera,
            "absorcion_por_empresa": absorcion_por_empresa,
        }
    }), 200
