"""Consulta autenticada de catálogos; no expone información personal."""
from flask import Blueprint, jsonify
from sqlalchemy import select
from database import db
from models.schema import TABLES
from core.security import login_required

catalogos_bp = Blueprint("catalogos_api", __name__)
CATALOGS = ("paises", "etnias", "departamentos", "municipios", "centros_educativos", "areas_carrera", "carreras", "becas")

@catalogos_bp.get("")
@login_required
def get_catalogos():
    data = {name: [dict(row) for row in db.session.execute(select(TABLES[name])).mappings()] for name in CATALOGS}
    return jsonify(success=True, **data)
