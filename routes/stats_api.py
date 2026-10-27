"""
===============================================================================
EVENTOS-UNI - API REST DE ESTADÍSTICAS Y MÉTRICAS INSTITUCIONALES (`/api/stats`)
===============================================================================
Proporciona endpoints RESTful para agregación de datos en tiempo real (SQL 5FN):
- GET /api/stats/evento/<evento_id> : Demografía de un evento (Género, Rol, Geografía, Carreras).
- GET /api/stats/globales          : Indicadores globales, Ejes Estratégicos y Dashboard Rector.
===============================================================================
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from database import db
from models.eventos import Asistencia, Actividad, ActividadLineamiento
from models.base import Persona, Estudiante, Trabajador
from models.catalogos import Sede, Ciudad, Departamento, Lineamiento, EjeLineamiento
from core.security import login_required
from extensions import cache

stats_bp = Blueprint("stats_api", __name__)


# -----------------------------------------------------------------------------
# 1. GET /api/stats/evento/<evento_id> - Estadísticas por Actividad
# -----------------------------------------------------------------------------

@stats_bp.route("/evento/<string:evento_id>", methods=["GET"])
@login_required
@cache.cached(timeout=10, query_string=True)
def get_stats_evento(evento_id: str):
    """
    Calcula las métricas demográficas de un evento específico en tiempo real
    cruzando las tablas normalizadas en 5FN (Persona, Estudiante, Trabajador, Geografía).
    """
    actividad = Actividad.query.get(evento_id)
    if not actividad:
        return jsonify({"success": False, "message": "Evento no encontrado"}), 404

    asistencias = Asistencia.query.filter_by(actividad_id=evento_id).all()
    total_asistentes = len(asistencias)

    if total_asistentes == 0:
        return jsonify({
            "success": True,
            "evento_id": evento_id,
            "total_asistentes": 0,
            "message": "No hay asistencias registradas para esta actividad aún",
            "genero": {"hombres": 0, "mujeres": 0, "hombres_cnt": 0, "mujeres_cnt": 0},
            "rol": {"estudiantes": 0, "trabajadores": 0, "otros": 0, "estudiantes_cnt": 0, "trabajadores_cnt": 0, "otros_cnt": 0},
            "carreras": [],
            "grupos": [],
            "anos_academicos": {},
            "geografia": {}
        }), 200

    # 1. Distribución por Género
    hombres_cnt = db.session.query(func.count(Asistencia.id))\
        .join(Persona, Asistencia.persona_id == Persona.id)\
        .filter(Asistencia.actividad_id == evento_id, Persona.sexo == "Masculino").scalar() or 0

    mujeres_cnt = total_asistentes - hombres_cnt

    # 2. Distribución por Rol Institucional
    estudiantes_cnt = db.session.query(func.count(Asistencia.id))\
        .join(Persona, Asistencia.persona_id == Persona.id)\
        .join(Estudiante, Persona.id == Estudiante.persona_id)\
        .filter(Asistencia.actividad_id == evento_id).scalar() or 0

    trabajadores_cnt = db.session.query(func.count(Asistencia.id))\
        .join(Persona, Asistencia.persona_id == Persona.id)\
        .join(Trabajador, Persona.id == Trabajador.persona_id)\
        .filter(Asistencia.actividad_id == evento_id).scalar() or 0

    otros_cnt = max(0, total_asistentes - (estudiantes_cnt + trabajadores_cnt))

    # 3. Distribución por Carrera Profesional
    carreras_raw = db.session.query(Estudiante.carrera, func.count(Asistencia.id))\
        .join(Persona, Estudiante.persona_id == Persona.id)\
        .join(Asistencia, Persona.id == Asistencia.persona_id)\
        .filter(Asistencia.actividad_id == evento_id)\
        .group_by(Estudiante.carrera).all()

    carreras = [
        {
            "carrera": c[0] or "General / Trabajadores",
            "count": c[1],
            "porcentaje": round((c[1] / total_asistentes) * 100, 1)
        }
        for c in carreras_raw
    ]

    # 4. Distribución por Grupo
    grupos_raw = db.session.query(Estudiante.grupo, func.count(Asistencia.id))\
        .join(Persona, Estudiante.persona_id == Persona.id)\
        .join(Asistencia, Persona.id == Asistencia.persona_id)\
        .filter(Asistencia.actividad_id == evento_id)\
        .group_by(Estudiante.grupo).all()

    grupos = [
        {
            "grupo": g[0] or "General",
            "count": g[1],
            "porcentaje": round((g[1] / total_asistentes) * 100, 1)
        }
        for g in grupos_raw
    ]

    # 5. Distribución por Año Académico
    anos_raw = db.session.query(Estudiante.ano_academico, func.count(Asistencia.id))\
        .join(Persona, Estudiante.persona_id == Persona.id)\
        .join(Asistencia, Persona.id == Asistencia.persona_id)\
        .filter(Asistencia.actividad_id == evento_id)\
        .group_by(Estudiante.ano_academico).all()

    anos_academicos = { (a[0] or "N/A"): a[1] for a in anos_raw }

    # 6. Distribución Geográfica (Procedencia por Departamento)
    geografia_raw = db.session.query(
        Departamento.nombre, func.count(Asistencia.id)
    ).join(Ciudad, Departamento.id == Ciudad.departamento_id)\
     .join(Persona, Ciudad.id == Persona.ciudad_procedencia_id)\
     .join(Asistencia, Persona.id == Asistencia.persona_id)\
     .filter(Asistencia.actividad_id == evento_id)\
     .group_by(Departamento.nombre).all()

    geografia_map = { (g[0] or "Managua"): g[1] for g in geografia_raw }
    if not geografia_map:
        geografia_map = {"Managua": total_asistentes}

    return jsonify({
        "success": True,
        "evento_id": evento_id,
        "total_asistentes": total_asistentes,
        "genero": {
            "hombres": round((hombres_cnt / total_asistentes) * 100, 1),
            "mujeres": round((mujeres_cnt / total_asistentes) * 100, 1),
            "hombres_cnt": hombres_cnt,
            "mujeres_cnt": mujeres_cnt
        },
        "rol": {
            "estudiantes": round((estudiantes_cnt / total_asistentes) * 100, 1),
            "trabajadores": round((trabajadores_cnt / total_asistentes) * 100, 1),
            "otros": round((otros_cnt / total_asistentes) * 100, 1),
            "estudiantes_cnt": estudiantes_cnt,
            "trabajadores_cnt": trabajadores_cnt,
            "otros_cnt": otros_cnt
        },
        "carreras": carreras,
        "grupos": grupos,
        "anos_academicos": anos_academicos,
        "geografia": geografia_map
    }), 200


# -----------------------------------------------------------------------------
# 2. GET /api/stats/globales - Dashboard Rectoral e Indicadores Globales
# -----------------------------------------------------------------------------

@stats_bp.route("/globales", methods=["GET"])
@login_required
@cache.cached(timeout=60, query_string=True)
def get_stats_globales():
    """
    Endpoint para el Dashboard del Rector. Agrupa métricas globales de toda la universidad:
    Geografía, Ejes de Estrategia Nacional 2026, Tipos de Persona y Carreras.
    """
    sede_codigo = request.args.get("recinto")  # ej. "RUSB", "RUPAP"

    query_actividades = Actividad.query
    query_asistencias = db.session.query(func.count(Asistencia.id)).join(Actividad)

    if sede_codigo:
        sede = Sede.query.filter_by(codigo=sede_codigo).first()
        if sede:
            query_asistencias = query_asistencias.join(Persona, Asistencia.persona_id == Persona.id)\
                .filter(Persona.sede_id == sede.id)

    total_eventos = query_actividades.count()
    total_asistencias = query_asistencias.scalar() or 0

    # 1. Agregación por Carrera Profesional
    carreras_stats = db.session.query(
        Estudiante.carrera, func.count(Asistencia.id)
    ).join(Persona, Estudiante.persona_id == Persona.id)\
     .join(Asistencia, Persona.id == Asistencia.persona_id)\
     .group_by(Estudiante.carrera).all()

    carreras_map = {carrera or "General": count for carrera, count in carreras_stats}

    # 2. Agregación por Procedencia Geográfica (Departamento)
    geografia_stats = db.session.query(
        Departamento.nombre, func.count(Asistencia.id)
    ).join(Ciudad, Departamento.id == Ciudad.departamento_id)\
     .join(Persona, Ciudad.id == Persona.ciudad_procedencia_id)\
     .join(Asistencia, Persona.id == Asistencia.persona_id)\
     .group_by(Departamento.nombre).all()

    geografia_map = {dept or "Managua": count for dept, count in geografia_stats}
    if not geografia_map and total_asistencias > 0:
        geografia_map = {"Managua": total_asistencias}

    # 3. Alineación con Ejes de la Estrategia Nacional 2026
    ejes_stats = db.session.query(
        EjeLineamiento.nombre, func.count(ActividadLineamiento.id)
    ).join(Lineamiento, EjeLineamiento.id == Lineamiento.eje_id)\
     .join(ActividadLineamiento, Lineamiento.id == ActividadLineamiento.lineamiento_id)\
     .group_by(EjeLineamiento.nombre).all()

    ejes_map = {eje or "Eje General": count for eje, count in ejes_stats}

    # 4. Composición de Asistentes por Tipo de Persona
    estudiantes_total = db.session.query(func.count(Asistencia.id))\
        .join(Persona, Asistencia.persona_id == Persona.id)\
        .join(Estudiante, Persona.id == Estudiante.persona_id).scalar() or 0

    trabajadores_total = db.session.query(func.count(Asistencia.id))\
        .join(Persona, Asistencia.persona_id == Persona.id)\
        .join(Trabajador, Persona.id == Trabajador.persona_id).scalar() or 0

    otros_total = max(0, total_asistencias - (estudiantes_total + trabajadores_total))

    return jsonify({
        "success": True,
        "resumen": {
            "total_eventos": total_eventos,
            "total_asistencias": total_asistencias
        },
        "distribucion_carreras": carreras_map,
        "distribucion_geografica": geografia_map,
        "ejes_estrategicos": ejes_map,
        "composicion_personas": {
            "estudiantes": estudiantes_total,
            "trabajadores": trabajadores_total,
            "otros": otros_total
        }
    }), 200