"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - API REST DE CATÁLOGOS (`/api/catalogos`)
===============================================================================
Proporciona el endpoint RESTful centralizado para alimentar selecciones dinámicas:
- GET /api/catalogos : Retorna departamentos, municipios, carreras, áreas,
  becas, países y etnias del padrón institucional.
===============================================================================
"""

from flask import Blueprint, jsonify
from models.catalogos import (
    Pais,
    Etnia,
    Departamento,
    Municipio,
    CentroEducativo,
    AreaCarrera,
    Carrera,
    Beca,
)
from core.security import login_required
from extensions import cache

catalogos_bp = Blueprint("catalogos_api", __name__)


# -----------------------------------------------------------------------------
# 1. GET /api/catalogos - Carga Unificada de Catálogos del Sistema
# -----------------------------------------------------------------------------

@catalogos_bp.route("", methods=["GET"])
@login_required
@cache.cached(timeout=3600)
def get_catalogos():
    """
    Retorna todos los catálogos base requeridos para poblar dinámicamente los campos
    <select> de los formularios del frontend (Filtro de ofertas, Perfil, etc.).
    Endpoint común accesible para todos los roles autenticados.
    """
    departamentos = Departamento.query.all()
    municipios = Municipio.query.all()
    carreras = Carrera.query.all()
    areas = AreaCarrera.query.all()
    becas = Beca.query.all()
    paises = Pais.query.all()
    etnias = Etnia.query.all()

    return jsonify({
        "success": True,
        "departamentos": [{"id": d.id_departamento, "id_departamento": d.id_departamento, "nombre": d.nombre} for d in departamentos],
        "municipios": [{"id": m.id_municipio, "id_municipio": m.id_municipio, "nombre": m.nombre, "id_departamento": m.id_departamento} for m in municipios],
        # Compatibilidad con vistas previas que esperaban "ciudades"
        "ciudades": [{"id": m.id_municipio, "nombre": m.nombre, "departamento_id": m.id_departamento} for m in municipios],
        "carreras": [{"id": c.id_carrera, "id_carrera": c.id_carrera, "nombre": c.nombre, "id_area": c.id_area} for c in carreras],
        "areas_carrera": [{"id": a.id_area, "id_area": a.id_area, "nombre": a.nombre} for a in areas],
        "becas": [{"id": b.id_beca, "id_beca": b.id_beca, "nombre": b.nombre, "tipo": b.tipo} for b in becas],
        "paises": [{"id": p.id_pais, "id_pais": p.id_pais, "nombre": p.nombre, "codigo_iso": p.codigo_iso} for p in paises],
        "etnias": [{"id": e.id_etnia, "id_etnia": e.id_etnia, "nombre": e.nombre} for e in etnias],
    }), 200
