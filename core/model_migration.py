"""Conversión transaccional del padrón anterior al modelo socioacadémico.

No convierte eventos en experiencias ni trabajadores en tutores por suposición.
La copia completa previa conserva los datos sin equivalencia y el esquema original.
"""
import re
import sqlalchemy as sa
from database import db
from models.schema import TABLES as T
from core.schema_rules import install_schema_rules

LEGACY_TABLES = {
    "acciones_estrategicas", "actividades", "actividades_lineamientos", "asistencias", "auth_sessions",
    "bitacoras_acciones", "ciudades", "conflictos_sincronizacion", "departamentos", "ejes_lineamiento",
    "espacios_fisicos", "estudiantes", "lineamientos", "lotes_sincronizacion", "nodos_cliente", "personas",
    "registro_consultas", "sedes", "tipos_actividad", "tombstones", "trabajadores", "unidades_organizativas", "usuarios",
}
ROLE_MAP = {"Rector": "Administrador", "Encargado": "Coordinador", "Asistencia": "Consulta"}


def migrate_model(connection, backup_verified=False):
    inspector = sa.inspect(connection)
    existing = set(inspector.get_table_names())
    if "personas" not in existing:
        db.metadata.create_all(connection)
        install_schema_rules(connection)
        return {"mode": "new", "tables": len(T)}
    if connection.dialect.name != "sqlite":
        raise RuntimeError("La conversión de datos heredados requiere SQLite. Preparar una migración de datos específica para una base heredada PostgreSQL.")
    if not backup_verified:
        raise RuntimeError("Se requiere un respaldo verificado: ejecutar scripts/migrate_database.py con la aplicación detenida.")
    unknown = existing - LEGACY_TABLES - {"alembic_version"}
    if unknown:
        raise RuntimeError("La base contiene tablas ajenas al esquema conocido; se cancela sin modificarla.")
    old = {name: [dict(r) for r in connection.exec_driver_sql(f'SELECT * FROM "{name}"').mappings()] for name in sorted(existing & LEGACY_TABLES)}
    persons = {r["id"]: r for r in old["personas"]}
    units = {r["id"]: r for r in old["unidades_organizativas"]}
    if any(u["rol"] not in set(ROLE_MAP) | {"Administrador", "Coordinador", "Tutor", "Supervisor", "Estudiante", "Consulta"} for u in old["usuarios"]):
        raise RuntimeError("Hay roles sin correspondencia; no se asignarán permisos por suposición.")
    # El respaldo se ha verificado antes; la transacción externa revierte todo si algo falla.
    for name in sorted(existing & LEGACY_TABLES):
        connection.exec_driver_sql(f'DROP TABLE "{name}"')
    db.metadata.create_all(connection)

    def insert(name, **values):
        result = connection.execute(T[name].insert().values(**values))
        return result.inserted_primary_key[0]

    departments, municipalities, areas, careers, students, users = {}, {}, {}, {}, {}, {}
    for row in old["departamentos"]:
        departments[row["id"]] = insert("departamentos", nombre=row["nombre"])
    for row in old["ciudades"]:
        municipalities[row["id"]] = insert("municipios", nombre=row["nombre"], id_departamento=departments[row["departamento_id"]])
    for row in old["estudiantes"]:
        p = persons[row["persona_id"]]
        # Los nombres antiguos no separados se conservan íntegros; no adivinar apellidos.
        sid = insert("estudiantes", cup=p["numero_unico"], cedula=p["cedula"],
                     nombre=p.get("nombres") or p["nombres_apellidos"], apellido=p.get("apellidos"), sexo=p["sexo"])
        students[p["id"]] = sid
        city_id = municipalities.get(p.get("ciudad_residencia_id"))
        if city_id:
            insert("direcciones_estudiante", id_estudiante=sid, id_municipio=city_id, es_principal=True)
        if row.get("carrera"):
            unit_id = row.get("area_conocimiento_id")
            if not unit_id or unit_id not in units:
                raise RuntimeError("No se puede asociar una carrera antigua a un área conocida.")
            area_name = units[unit_id]["nombre"]
            if area_name not in areas:
                areas[area_name] = insert("areas_carrera", nombre=area_name)
            career = row["carrera"]
            if career not in careers:
                careers[career] = insert("carreras", nombre=career, id_area=areas[area_name])
            grade = re.match(r"^(\d+)", row.get("ano_academico") or "")
            year = int(grade[1]) if grade and 1 <= int(grade[1]) <= 10 else None
            shift = row.get("turno")
            if shift not in {"Matutino", "Vespertino", "Nocturno", "Sabatino", "Dominical"}:
                shift = None
            insert("matriculas", id_estudiante=sid, id_carrera=careers[career], anio_academico=year,
                   grupo_clase=row.get("grupo"), turno=shift)

    for row in old["usuarios"]:
        role = ROLE_MAP.get(row["rol"], row["rol"])
        student_id = students.get(row.get("persona_id"))
        if role == "Estudiante" and not student_id:
            raise RuntimeError("Una cuenta de estudiante no tiene identidad vinculada; se cancela para evitar asociaciones inseguras.")
        if role in {"Tutor", "Supervisor"}:
            raise RuntimeError("La identidad de tutores o supervisores debe migrarse explícitamente.")
        uid = insert("usuarios", nombre_usuario="usr_" + row["id"].replace("-", ""),
                     email=row["email"].lower(), password_hash=row["password_hash"], rol=role,
                     id_estudiante=student_id, activo=True)
        users[row["id"]] = uid

    # Las sesiones anteriores se invalidan: los identificadores de cuenta cambiaron de UUID a entero.
    install_schema_rules(connection)
    if connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall():
        raise RuntimeError("La migración produciría referencias inválidas.")
    return {"mode": "legacy", "source_counts": {k: len(v) for k, v in old.items()},
            "target_counts": {k: connection.execute(sa.select(sa.func.count()).select_from(t)).scalar_one() for k,t in T.items()},
            "student_id_mapping": students, "user_id_mapping": users,
            "notes": ["Las filas y campos sin equivalencia permanecen en el respaldo completo.",
                      "Los datos personales desconocidos y períodos académicos quedan pendientes.",
                      "Las sesiones anteriores quedan revocadas."]}
