"""
===============================================================================
EVENTOS-UNI - API REST DE GESTIÓN DE ACTIVIDADES Y EVENTOS (`/api/eventos`)
===============================================================================
Proporciona endpoints RESTful CRUD para el ciclo de vida de los eventos:
- GET    /api/eventos             : Listado completo formateado para carruseles.
- GET    /api/eventos/<evento_id> : Consulta individual por ID con lineamientos.
- POST   /api/eventos             : Creación con validación estricta (máx 4 lineamientos).
- PATCH  /api/eventos/<evento_id> : Edición parcial con actualización de lineamientos.
- DELETE /api/eventos/<evento_id> : Eliminación (solo Rector/Encargado, solo sin asistentes).
===============================================================================
"""

import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session
from database import db
from models.eventos import Actividad, ActividadLineamiento
from models.catalogos import EspacioFisico, TipoActividad, UnidadOrganizativa, Lineamiento
from models.base import Usuario
from core.security import login_required, roles_required
from core.validators import validate_iso_date, validate_iso_time, sanitize_string
from extensions import cache

eventos_bp = Blueprint("eventos_api", __name__)


# -----------------------------------------------------------------------------
# 1. GET /api/eventos - Listado General de Actividades
# -----------------------------------------------------------------------------

def format_evento_dict(act: Actividad) -> dict:
    """Formatea una entidad Actividad a un diccionario JSON completo consumible por el frontend."""
    conteo_asistentes = len(act.asistencias) if act.asistencias else 0
    espacio = act.espacio_fisico
    capacidad_max = espacio.capacidad if espacio else 0
    sede = espacio.sede if espacio else None
    tipo = act.tipo
    unidad = act.unidad_responsable
    creador = act.creador

    f_ini_str = str(act.fecha_inicio) if act.fecha_inicio is not None else ""
    f_fin_str = str(act.fecha_fin) if act.fecha_fin is not None else ""
    h_ini_str = str(act.hora_inicio) if act.hora_inicio is not None else ""
    h_fin_str = str(act.hora_fin) if act.hora_fin is not None else ""

    return {
        "id": act.id,
        "codigo_actividad": act.codigo_actividad,
        "title": act.nombre,
        "status": act.calcular_status(),
        "tags": [
            tipo.nombre if tipo else "General",
            unidad.codigo if unidad else "UNI"
        ],
        "date": f"{f_ini_str} a {f_fin_str}",
        "time": f"{h_ini_str} - {h_fin_str}",
        "location": f"{sede.nombre}, {espacio.nombre}" if (sede and espacio) else (espacio.nombre if espacio else "Por definir"),
        "lugar": espacio.nombre if espacio else "Por definir",
        "recinto": sede.codigo if sede else "Por definir",
        "sede_id": espacio.sede_id if espacio else None,
        "espacio_fisico_id": act.espacio_fisico_id,
        "unidad_responsable_id": act.unidad_responsable_id,
        "tipo_actividad_id": act.tipo_actividad_id,
        "coordinator": creador.email if creador else "Sin asignar",
        "capacity": f"{conteo_asistentes} / {capacidad_max} Asistentes",
        "image": act.imagen_url or "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80",
        "imagen_url": act.imagen_url or "",
        "description": act.proposito or "",
        "proposito": act.proposito or "",
        "dateStartISO": f_ini_str,
        "dateEndISO": f_fin_str,
        "timeStartISO": h_ini_str,
        "timeEndISO": h_fin_str,
        "type": tipo.nombre if tipo else "",
        "area": unidad.codigo if unidad else "",
        "is_synced": act.is_synced,
        "created_offline": act.created_offline,
        "total_asistentes": conteo_asistentes,
        "capacidad_maxima": capacidad_max,
        "lineamientos": [
            {
                "id": al.lineamiento.id if al.lineamiento else al.lineamiento_id,
                "eje_id": al.lineamiento.eje_id if al.lineamiento else None,
                "eje_nombre": al.lineamiento.eje.nombre if (al.lineamiento and al.lineamiento.eje) else None,
                "numero_oficial": al.lineamiento.numero_oficial if al.lineamiento else None,
                "descripcion": al.lineamiento.descripcion if al.lineamiento else None,
                "justificacion": al.justificacion or ""
            }
            for al in act.lineamientos_asociados
        ] if act.lineamientos_asociados else []
    }


@eventos_bp.route("", methods=["GET"])
@login_required
def get_eventos():
    """
    Retorna la lista de todas las actividades ordenadas por fecha descendente,
    mapeadas con el formato JSON consumido por los carruseles del frontend.
    """
    actividades = Actividad.query.order_by(Actividad.fecha_inicio.desc()).all()
    lista_eventos = [format_evento_dict(act) for act in actividades]
    return jsonify(lista_eventos), 200


# -----------------------------------------------------------------------------
# 2. GET /api/eventos/<evento_id> - Consulta Detallada por ID
# -----------------------------------------------------------------------------

@eventos_bp.route("/<string:evento_id>", methods=["GET"])
@login_required
def get_evento_by_id(evento_id: str):
    """Retorna la información completa de una actividad específica por su UUID."""
    act = Actividad.query.get(evento_id)
    if not act:
        return jsonify({"success": False, "message": "Actividad no encontrada"}), 404

    return jsonify(format_evento_dict(act)), 200


# -----------------------------------------------------------------------------
# 3. POST /api/eventos - Creación de Actividades
# -----------------------------------------------------------------------------

@eventos_bp.route("", methods=["POST"])
@login_required
@roles_required("Rector", "Encargado")
def create_evento():
    """
    Crea una nueva actividad universitaria con validación estricta de campos
    obligatorios, formatos ISO y límite de máximo 4 lineamientos estratégicos.
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Payload inválido o vacío"}), 400

    errors = {}

    # --- Validación de título ---
    title = sanitize_string(data.get("title", ""), max_length=200)
    if not title:
        errors["title"] = "El nombre del evento es obligatorio."

    # --- Validación de fecha de inicio ---
    date_start = data.get("dateStartISO", "").strip()
    if not date_start:
        errors["dateStartISO"] = "La fecha de inicio es obligatoria."
    elif not validate_iso_date(date_start):
        errors["dateStartISO"] = "La fecha de inicio debe tener formato YYYY-MM-DD."

    # --- Validación de fecha de fin ---
    date_end = data.get("dateEndISO", "").strip()
    if date_end:
        if not validate_iso_date(date_end):
            errors["dateEndISO"] = "La fecha de cierre debe tener formato YYYY-MM-DD."
        elif date_start and validate_iso_date(date_start) and date_end < date_start:
            errors["dateEndISO"] = "La fecha de cierre no puede ser anterior a la fecha de inicio."

    # --- Validación de hora de inicio ---
    time_start = data.get("timeStartISO", "").strip()
    if time_start and not validate_iso_time(time_start):
        errors["timeStartISO"] = "La hora de inicio debe tener formato HH:MM."

    # --- Validación de hora de fin ---
    time_end = data.get("timeEndISO", "").strip()
    if time_end:
        if not validate_iso_time(time_end):
            errors["timeEndISO"] = "La hora de cierre debe tener formato HH:MM."
        elif time_start and validate_iso_time(time_start) and time_end < time_start:
            errors["timeEndISO"] = "La hora de cierre no puede ser anterior a la hora de inicio."

    # --- Validación de lineamientos (máximo 4) ---
    lineamientos_input = data.get("lineamientos") or []
    if isinstance(lineamientos_input, list) and len(lineamientos_input) > 4:
        errors["lineamientos"] = "Se pueden asociar un máximo de 4 lineamientos estratégicos por actividad."

    if errors:
        return jsonify({"success": False, "message": "Errores de validación", "errors": errors}), 400

    nuevo_id = data.get("id") or str(uuid.uuid4())

    # Resolución flexible de Tipo de Actividad
    tipo_id = data.get("tipo_actividad_id")
    if tipo_id:
        t_obj = TipoActividad.query.get(tipo_id)
        if not t_obj:
            t_obj = TipoActividad.query.filter_by(nombre=tipo_id).first()
            tipo_id = t_obj.id if t_obj else None
    if not tipo_id and data.get("type"):
        t_obj = TipoActividad.query.filter_by(nombre=data.get("type")).first()
        if t_obj:
            tipo_id = t_obj.id

    # Resolución flexible de Unidad Responsable
    unidad_id = data.get("unidad_responsable_id")
    if unidad_id:
        u_obj = UnidadOrganizativa.query.get(unidad_id)
        if not u_obj:
            u_obj = UnidadOrganizativa.query.filter(
                (UnidadOrganizativa.codigo == unidad_id) | (UnidadOrganizativa.nombre == unidad_id)
            ).first()
            unidad_id = u_obj.id if u_obj else None
    if not unidad_id and data.get("area"):
        u_obj = UnidadOrganizativa.query.filter(
            (UnidadOrganizativa.codigo == data.get("area")) | (UnidadOrganizativa.nombre == data.get("area"))
        ).first()
        if u_obj:
            unidad_id = u_obj.id

    # Resolución flexible de Espacio Físico
    espacio_id = data.get("espacio_fisico_id")
    if espacio_id:
        e_obj = EspacioFisico.query.get(espacio_id)
        if not e_obj:
            e_obj = EspacioFisico.query.filter(
                EspacioFisico.nombre.ilike(f"%{espacio_id}%")
            ).first()
            espacio_id = e_obj.id if e_obj else None

    # Fallbacks de respaldo si los catálogos están vacíos o no coincidieron
    if not tipo_id:
        t = TipoActividad.query.first()
        if t: tipo_id = t.id
    if not unidad_id:
        u = UnidadOrganizativa.query.first()
        if u: unidad_id = u.id
    if not espacio_id:
        e = EspacioFisico.query.first()
        if e: espacio_id = e.id

    creador_id = session.get("user_id")
    if not creador_id:
        usr = Usuario.query.first()
        if usr: creador_id = usr.id

    nueva_actividad = Actividad(
        id=str(nuevo_id),
        codigo_actividad=data.get("codigo_actividad") or f"ACT-{int(datetime.now(timezone.utc).timestamp())}",
        nombre=title,
        tipo_actividad_id=tipo_id,
        unidad_responsable_id=unidad_id,
        usuario_creador_id=creador_id,
        espacio_fisico_id=espacio_id,
        proposito=sanitize_string(data.get("description", ""), max_length=1000),
        imagen_url=data.get("imagen_url") or data.get("image"),
        fecha_inicio=date_start,
        fecha_fin=date_end or date_start,
        hora_inicio=time_start or "08:00:00",
        hora_fin=time_end or "16:00:00",
        is_synced=data.get("is_synced", 1),
        created_offline=data.get("created_offline", 0),
        updated_at=datetime.now(timezone.utc).isoformat()
    )

    db.session.add(nueva_actividad)

    # Registro de lineamientos asociados (máximo 4)
    if isinstance(lineamientos_input, list):
        for item in lineamientos_input[:4]:
            l_id = item.get("lineamiento_id") if isinstance(item, dict) else item
            just = item.get("justificacion") if isinstance(item, dict) else ""
            
            lin_obj = Lineamiento.query.get(l_id) if l_id else None
            if not lin_obj and l_id:
                lin_obj = Lineamiento.query.filter_by(numero_oficial=l_id).first()

            if lin_obj and just and str(just).strip():
                assoc = ActividadLineamiento(
                    id=str(uuid.uuid4()),
                    actividad_id=nueva_actividad.id,
                    lineamiento_id=lin_obj.id,
                    justificacion=sanitize_string(str(just).strip(), max_length=500)
                )
                db.session.add(assoc)

    db.session.commit()
    cache.clear()

    return jsonify({
        "success": True,
        "message": "Actividad creada exitosamente",
        "id": nueva_actividad.id,
        "evento": format_evento_dict(nueva_actividad)
    }), 201


# -----------------------------------------------------------------------------
# 4. PATCH / PUT /api/eventos/<evento_id> - Actualización Parcial
# -----------------------------------------------------------------------------

@eventos_bp.route("/<string:evento_id>", methods=["PUT", "PATCH"])
@login_required
@roles_required("Rector", "Encargado")
def update_evento(evento_id: str):
    """
    Actualiza los datos de un evento existente incluyendo sus lineamientos.
    Bloquea la edición de eventos con status 'pasados'.
    """
    act = Actividad.query.get(evento_id)
    if not act:
        return jsonify({"success": False, "message": "Actividad no encontrada"}), 404

    if act.calcular_status() == "pasados":
        return jsonify({
            "success": False,
            "message": "No se puede editar una actividad que ya ha finalizado."
        }), 409

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Payload inválido"}), 400

    errors = {}

    if "title" in data:
        title = sanitize_string(data["title"], max_length=200)
        if not title:
            errors["title"] = "El nombre del evento no puede estar vacío."
        else:
            act.nombre = title

    if "description" in data:
        act.proposito = sanitize_string(data["description"], max_length=1000)

    new_date_start = data.get("dateStartISO", act.fecha_inicio)
    new_date_end   = data.get("dateEndISO", act.fecha_fin)

    if "dateStartISO" in data:
        if not validate_iso_date(data["dateStartISO"]):
            errors["dateStartISO"] = "La fecha de inicio debe tener formato YYYY-MM-DD."
        else:
            new_date_start = data["dateStartISO"]

    if "dateEndISO" in data and data["dateEndISO"]:
        if not validate_iso_date(data["dateEndISO"]):
            errors["dateEndISO"] = "La fecha de cierre debe tener formato YYYY-MM-DD."
        elif data["dateEndISO"] < new_date_start:
            errors["dateEndISO"] = "La fecha de cierre no puede ser anterior a la fecha de inicio."
        else:
            new_date_end = data["dateEndISO"]

    new_time_start = data.get("timeStartISO", act.hora_inicio)
    new_time_end   = data.get("timeEndISO", act.hora_fin)

    if "timeStartISO" in data and data["timeStartISO"]:
        if not validate_iso_time(data["timeStartISO"]):
            errors["timeStartISO"] = "La hora de inicio debe tener formato HH:MM."
        else:
            new_time_start = data["timeStartISO"]

    if "timeEndISO" in data and data["timeEndISO"]:
        if not validate_iso_time(data["timeEndISO"]):
            errors["timeEndISO"] = "La hora de cierre debe tener formato HH:MM."
        elif data["timeEndISO"] < new_time_start:
            errors["timeEndISO"] = "La hora de cierre no puede ser anterior a la hora de inicio."
        else:
            new_time_end = data["timeEndISO"]

    if "lineamientos" in data:
        lineamientos_input = data["lineamientos"] or []
        if isinstance(lineamientos_input, list):
            if len(lineamientos_input) > 4:
                errors["lineamientos"] = "Se pueden asociar un máximo de 4 lineamientos estratégicos por actividad."
            for item in lineamientos_input:
                just = item.get("justificacion") if isinstance(item, dict) else ""
                if not just or not str(just).strip():
                    errors["lineamientos"] = "Debe redactar la justificación para cada lineamiento seleccionado."
                    break

    if errors:
        return jsonify({"success": False, "message": "Errores de validación", "errors": errors}), 400

    act.fecha_inicio = new_date_start
    act.fecha_fin    = new_date_end
    act.hora_inicio  = new_time_start
    act.hora_fin     = new_time_end

    if "tipo_actividad_id" in data and data["tipo_actividad_id"]:
        t_val = data["tipo_actividad_id"]
        t_obj = TipoActividad.query.get(t_val) or TipoActividad.query.filter_by(nombre=t_val).first()
        if t_obj: act.tipo_actividad_id = t_obj.id

    if "unidad_responsable_id" in data and data["unidad_responsable_id"]:
        u_val = data["unidad_responsable_id"]
        u_obj = UnidadOrganizativa.query.get(u_val) or UnidadOrganizativa.query.filter(
            (UnidadOrganizativa.codigo == u_val) | (UnidadOrganizativa.nombre == u_val)
        ).first()
        if u_obj: act.unidad_responsable_id = u_obj.id

    if "espacio_fisico_id" in data and data["espacio_fisico_id"]:
        e_val = data["espacio_fisico_id"]
        e_obj = EspacioFisico.query.get(e_val) or EspacioFisico.query.filter(
            EspacioFisico.nombre.ilike(f"%{e_val}%")
        ).first()
        if e_obj: act.espacio_fisico_id = e_obj.id

    if "imagen_url" in data:
        act.imagen_url = data["imagen_url"]
    elif "image" in data:
        act.imagen_url = data["image"]

    # Actualizar asociaciones de lineamientos si se recibieron
    if "lineamientos" in data:
        ActividadLineamiento.query.filter_by(actividad_id=act.id).delete()
        lineamientos_input = data["lineamientos"] or []
        if isinstance(lineamientos_input, list):
            for item in lineamientos_input[:4]:
                l_id = item.get("lineamiento_id") if isinstance(item, dict) else item
                just = item.get("justificacion") if isinstance(item, dict) else ""

                lin_obj = Lineamiento.query.get(l_id) if l_id else None
                if not lin_obj and l_id:
                    lin_obj = Lineamiento.query.filter_by(numero_oficial=l_id).first()

                if lin_obj and just and str(just).strip():
                    assoc = ActividadLineamiento(
                        id=str(uuid.uuid4()),
                        actividad_id=act.id,
                        lineamiento_id=lin_obj.id,
                        justificacion=sanitize_string(str(just).strip(), max_length=500)
                    )
                    db.session.add(assoc)

    act.updated_at = datetime.now(timezone.utc).isoformat()
    db.session.commit()

    cache.clear()

    return jsonify({
        "success": True,
        "message": "Actividad actualizada correctamente",
        "evento": format_evento_dict(act)
    }), 200


# -----------------------------------------------------------------------------
# 5. DELETE /api/eventos/<evento_id> - Eliminación de Actividad
# -----------------------------------------------------------------------------

@eventos_bp.route("/<string:evento_id>", methods=["DELETE"])
@login_required
@roles_required("Rector", "Encargado")
def delete_evento(evento_id: str):
    """
    Elimina una actividad universitaria.
    Bloquea la eliminación si el evento tiene asistentes registrados o no está programado.
    """
    act = Actividad.query.get(evento_id)
    if not act:
        return jsonify({"success": False, "message": "Actividad no encontrada"}), 404

    status = act.calcular_status()
    if status == "activos":
        return jsonify({
            "success": False,
            "message": "No se puede eliminar una actividad que está en curso."
        }), 409

    if status == "pasados":
        return jsonify({
            "success": False,
            "message": "No se puede eliminar una actividad que ya ha finalizado."
        }), 409

    total_asistentes = len(act.asistencias)
    if total_asistentes > 0:
        return jsonify({
            "success": False,
            "message": f"No se puede eliminar: la actividad tiene {total_asistentes} asistente(s) registrado(s)."
        }), 409

    db.session.delete(act)
    db.session.commit()

    cache.clear()

    return jsonify({"success": True, "message": "Actividad eliminada correctamente"}), 200


# -----------------------------------------------------------------------------
# 6. POST /api/eventos/<evento_id>/activar - Activación Manual de Actividad
# -----------------------------------------------------------------------------

@eventos_bp.route("/<string:evento_id>/activar", methods=["POST"])
@login_required
@roles_required("Rector", "Encargado")
def activar_evento(evento_id: str):
    """Activa manualmente una actividad programada ajustando sus fechas al día de hoy."""
    from datetime import date as date_cls
    act = Actividad.query.get(evento_id)
    if not act:
        return jsonify({"success": False, "message": "Actividad no encontrada"}), 404

    if act.calcular_status() != "programados":
        return jsonify({
            "success": False,
            "message": "Solo se pueden activar manualmente actividades en estado 'Programados'."
        }), 409

    today_str = date_cls.today().isoformat()

    act.fecha_inicio = today_str
    if str(act.fecha_fin) < today_str:
        act.fecha_fin = today_str

    act.updated_at = datetime.now(timezone.utc).isoformat()
    db.session.commit()
    cache.clear()

    return jsonify({
        "success": True,
        "message": "Actividad activada exitosamente",
        "evento": format_evento_dict(act)
    }), 200


# -----------------------------------------------------------------------------
# 7. POST /api/eventos/<evento_id>/finalizar - Finalización Manual de Actividad
# -----------------------------------------------------------------------------

@eventos_bp.route("/<string:evento_id>/finalizar", methods=["POST"])
@login_required
@roles_required("Rector", "Encargado")
def finalizar_evento(evento_id: str):
    """Finaliza manualmente una actividad activa pasándola al día de ayer."""
    from datetime import date as date_cls, timedelta
    act = Actividad.query.get(evento_id)
    if not act:
        return jsonify({"success": False, "message": "Actividad no encontrada"}), 404

    if act.calcular_status() != "activos":
        return jsonify({
            "success": False,
            "message": "Solo se pueden finalizar actividades que estén en estado 'Activos'."
        }), 409

    yesterday_str = (date_cls.today() - timedelta(days=1)).isoformat()

    act.fecha_inicio = yesterday_str
    act.fecha_fin    = yesterday_str
    act.updated_at   = datetime.now(timezone.utc).isoformat()
    db.session.commit()
    cache.clear()

    return jsonify({
        "success": True,
        "message": "Actividad finalizada exitosamente",
        "evento": format_evento_dict(act)
    }), 200