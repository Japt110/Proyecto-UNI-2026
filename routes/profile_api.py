"""Perfil del usuario autenticado; nunca acepta identificadores de otro estudiante."""
from flask import Blueprint, jsonify, g
from sqlalchemy import select
from core.security import login_required
from database import db
from models.schema import TABLES as T

profile_bp = Blueprint("profile_api", __name__)

def profile_data(user):
    student = user.estudiante
    data = dict(email=user.email, nombre_usuario=user.nombre_usuario, rol=user.rol,
                nombre=user.nombre_visible, apellido="", cup="", cedula="", carrera="", anio="",
                modalidad="", telefono="", ciudad="", estado_matricula="", direccion="",
                sexo="", fecha_nacimiento=None, edad=None,
                foto_registrada=bool(user.ruta_imagen), dimension_nacional="", id_pais_origen=None,
                id_etnia=None, estado_civil="", hijos=None, tipo_telefono="", telefono_principal=None,
                id_departamento=None, id_municipio=None, comunidad="", zona="", direccion_principal=None,
                id_centro_educativo=None, educacion_tecnica="", titulo_obtenido="", anio_graduacion=None,
                id_carrera=None, periodo_academico="", turno="", grupo_clase="", id_beca=None)
    if not student:
        return data
    data.update(nombre=student.nombre, apellido=student.apellido or "", cup=student.cup, cedula=student.cedula,
                sexo=student.sexo, fecha_nacimiento=student.fecha_nacimiento.isoformat() if student.fecha_nacimiento else None,
                edad=student.edad_actual)
    for key in ("dimension_nacional", "id_pais_origen", "id_etnia", "estado_civil", "hijos"):
        data[key] = getattr(student, key)
    mat, carrera = T["matriculas"], T["carreras"]
    row = db.session.execute(select(mat, carrera.c.nombre.label("nombre_carrera")).join(carrera).where(
        mat.c.id_estudiante == student.id_estudiante).order_by((mat.c.estado == "Activa").desc(), mat.c.id_matricula.desc()).limit(1)).mappings().first()
    if row:
        data.update(carrera=row["nombre_carrera"], id_carrera=row["id_carrera"], anio=row["anio_academico"] or "",
                    modalidad=row["modalidad"] or "", estado_matricula=row["estado"],
                    periodo_academico=row["periodo_academico"] or "", turno=row["turno"] or "",
                    grupo_clase=row["grupo_clase"] or "", id_beca=row["id_beca"])
    phone = T["telefonos_estudiante"]
    row = db.session.execute(select(phone).where(phone.c.id_estudiante == student.id_estudiante).order_by(phone.c.es_principal.desc(),phone.c.id_telefono).limit(1)).mappings().first()
    if row:
        data.update(telefono=row["numero"], tipo_telefono=row["tipo"], telefono_principal=row["es_principal"])
    address, city = T["direcciones_estudiante"], T["municipios"]
    row = db.session.execute(select(address, city.c.nombre.label("ciudad"), city.c.id_departamento).join(city).where(address.c.id_estudiante == student.id_estudiante).order_by(address.c.es_principal.desc(),address.c.id_direccion).limit(1)).mappings().first()
    if row:
        data.update(ciudad=row["ciudad"], direccion=row["direccion_domiciliar"] or "",
                    id_departamento=row["id_departamento"], id_municipio=row["id_municipio"],
                    comunidad=row["comunidad"] or "", zona=row["zona"] or "", direccion_principal=row["es_principal"])
    education = T["educacion_previa_estudiante"]
    row = db.session.execute(select(education).where(education.c.id_estudiante == student.id_estudiante)
                             .order_by(education.c.id_educacion.desc()).limit(1)).mappings().first()
    if row:
        for key in ("id_centro_educativo", "educacion_tecnica", "titulo_obtenido", "anio_graduacion"):
            data[key] = row[key]
    return data


def profile_options(profile):
    """Opciones de los catálogos reales, sin inventar registros faltantes."""
    catalogs = {}
    for name, key in (("paises", "id_pais"), ("etnias", "id_etnia"),
                      ("departamentos", "id_departamento"), ("municipios", "id_municipio"),
                      ("centros_educativos", "id_centro"), ("carreras", "id_carrera"), ("becas", "id_beca")):
        table = T[name]
        query = select(table.c[key], table.c.nombre).order_by(table.c.nombre, table.c[key])
        if name == "municipios":
            query = query.where(table.c.id_departamento == profile["id_departamento"])
        catalogs[name] = [(row[0], row[1]) for row in db.session.execute(query)]
    catalogs["municipios_por_departamento"] = [dict(row) for row in db.session.execute(
        select(T["municipios"]).order_by(T["municipios"].c.nombre)).mappings()]
    return catalogs

@profile_bp.get("")
@login_required
def get_profile():
    return jsonify(success=True, profile=profile_data(g.current_user))
