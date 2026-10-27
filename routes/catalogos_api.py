"""
===============================================================================
EVENTOS-UNI - API REST DE CATÁLOGOS INSTITUCIONALES, GEOGRÁFICOS Y ESTRATÉGICOS (`/api/catalogos`)
===============================================================================
Proporciona el endpoint RESTful centralizado para alimentar selecciones dinámicas:
- GET /api/catalogos : Retorna sedes, espacios físicos, unidades, tipos de actividad,
  departamentos, ciudades y ejes/lineamientos estratégicos.
===============================================================================
"""

from flask import Blueprint, jsonify
from models.catalogos import (
    Departamento,
    Ciudad,
    Sede,
    EspacioFisico,
    UnidadOrganizativa,
    TipoActividad,
    EjeLineamiento,
    Lineamiento,
)
from core.security import login_required
from extensions import cache

catalogos_bp = Blueprint("catalogos_api", __name__)


# -----------------------------------------------------------------------------
# 1. GET /api/catalogos - Carga Unificada de Catálogos
# -----------------------------------------------------------------------------

@catalogos_bp.route("", methods=["GET"])
@login_required
@cache.cached(timeout=3600)
def get_catalogos():
    """
    Retorna todos los catálogos base requeridos para poblar dinámicamente los campos
    <select> de los formularios del frontend (Crear Actividad, Edición, Filtros).
    """
    departamentos = Departamento.query.all()
    ciudades = Ciudad.query.all()
    sedes = Sede.query.all()
    espacios = EspacioFisico.query.all()
    unidades = UnidadOrganizativa.query.all()
    tipos = TipoActividad.query.all()
    ejes = EjeLineamiento.query.all()

    return jsonify({
        "success": True,
        "departamentos": [{"id": d.id, "nombre": d.nombre} for d in departamentos],
        "ciudades": [{"id": c.id, "nombre": c.nombre, "departamento_id": c.departamento_id} for c in ciudades],
        "sedes": [{"id": s.id, "nombre": s.nombre, "codigo": s.codigo, "ciudad_id": s.ciudad_id} for s in sedes],
        "espacios": [{"id": e.id, "sede_id": e.sede_id, "nombre": e.nombre, "capacidad": e.capacidad} for e in espacios],
        "unidades": [{"id": u.id, "nombre": u.nombre, "codigo": u.codigo, "nivel": u.nivel_jerarquico} for u in unidades],
        "tipos": [{"id": t.id, "nombre": t.nombre, "descripcion": t.descripcion} for t in tipos],
        "ejes": [{
            "id": ej.id,
            "numero_oficial": ej.numero_oficial,
            "nombre": ej.nombre,
            "descripcion": ej.descripcion,
            "lineamientos": [{
                "id": l.id,
                "numero_oficial": l.numero_oficial,
                "descripcion": l.descripcion
            } for l in ej.lineamientos]
        } for ej in ejes]
    }), 200
