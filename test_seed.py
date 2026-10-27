"""
===============================================================================
EVENTOS-UNI - SCRIPT DE SEMILLA DE PRUEBA Y DEBUGGING DE ESTUDIANTES (test_seed.py)
===============================================================================
Puebla la base de datos local (app_local.db) con un conjunto variado de estudiantes
de prueba (cédula, NUP, carné, carrera, grupo y sede) listos para realizar pruebas
de escaneo (3nStar Sc050), búsqueda filtrada y toma de asistencias en eventos activos.
===============================================================================
"""

import uuid
from datetime import datetime, timezone
from app import create_app
from database import db
from models.catalogos import Sede, UnidadOrganizativa, Ciudad
from models.base import Persona, Estudiante
from seed import seed_database

# Estudiantes de prueba para debugging
DEBUG_STUDENTS_DATA = [
    {
        "nup": "NUP-2026-101",
        "cedula": "001-120503-1004A",
        "nombres": "María Fernanda López Jarquín",
        "sexo": "Femenino",
        "carnet": "2022-0104U",
        "carrera": "Ingeniería de Sistemas",
        "ano": "4º Año",
        "grupo": "4M1-CO",
        "turno": "Diurno"
    },
    {
        "nup": "NUP-2026-102",
        "cedula": "001-180902-1015B",
        "nombres": "Kevin Alexander Gutiérrez Ruiz",
        "sexo": "Masculino",
        "carnet": "2023-0512U",
        "carrera": "Ingeniería de Sistemas",
        "ano": "3º Año",
        "grupo": "3M1-CO",
        "turno": "Diurno"
    },
    {
        "nup": "NUP-2026-103",
        "cedula": "001-251101-1088C",
        "nombres": "Sofía Valentina Ramírez Zelaya",
        "sexo": "Femenino",
        "carnet": "2024-0044U",
        "carrera": "Ingeniería Mecánica",
        "ano": "2º Año",
        "grupo": "1M1-ME",
        "turno": "Diurno"
    },
    {
        "nup": "NUP-2026-104",
        "cedula": "001-040200-1092D",
        "nombres": "Jorge Luis Bermúdez Castillo",
        "sexo": "Masculino",
        "carnet": "2021-0089U",
        "carrera": "Ingeniería Mecánica",
        "ano": "5º Año",
        "grupo": "1M1-ME",
        "turno": "Diurno"
    },
    {
        "nup": "NUP-2026-105",
        "cedula": "001-300603-1050E",
        "nombres": "Camila Andrea Mendoza Torrez",
        "sexo": "Femenino",
        "carnet": "2022-0331U",
        "carrera": "Ingeniería Industrial",
        "ano": "4º Año",
        "grupo": "3M1-IND",
        "turno": "Diurno"
    },
    {
        "nup": "NUP-2026-106",
        "cedula": "001-140702-1061F",
        "nombres": "Diego Armando Fonseca Morales",
        "sexo": "Masculino",
        "carnet": "2023-0198U",
        "carrera": "Ingeniería Industrial",
        "ano": "3º Año",
        "grupo": "3M1-IND",
        "turno": "Diurno"
    },
    {
        "nup": "NUP-2026-107",
        "cedula": "001-190104-1033G",
        "nombres": "Lucía Isabel Blandón Silva",
        "sexo": "Femenino",
        "carnet": "2024-0711U",
        "carrera": "Arquitectura",
        "ano": "1º Año",
        "grupo": "2M1-ARQ",
        "turno": "Diurno"
    },
    {
        "nup": "NUP-2026-108",
        "cedula": "001-081001-1022H",
        "nombres": "Gabriel Ernesto Espinoza Cruz",
        "sexo": "Masculino",
        "carnet": "2021-0415U",
        "carrera": "Arquitectura",
        "ano": "5º Año",
        "grupo": "2M1-ARQ",
        "turno": "Diurno"
    },
    {
        "nup": "NUP-2026-109",
        "cedula": "001-111103-1077J",
        "nombres": "Valeria Nicole Sevilla Hernández",
        "sexo": "Femenino",
        "carnet": "2023-0660U",
        "carrera": "Ingeniería de Sistemas",
        "ano": "3º Año",
        "grupo": "1M1-SO",
        "turno": "Nocturno"
    },
    {
        "nup": "NUP-2026-110",
        "cedula": "001-220402-1011K",
        "nombres": "Javier Enrique Solís Rocha",
        "sexo": "Masculino",
        "carnet": "2022-0982U",
        "carrera": "Ingeniería de Sistemas",
        "ano": "4º Año",
        "grupo": "1M1-SO",
        "turno": "Nocturno"
    }
]

app = create_app()

def populate_test_students():
    # 1. Primero sembrar la estructura base
    seed_database()

    with app.app_context():
        print("\n[+] Insertando estudiantes de debugging en el padrón 5FN...")
        
        sede = Sede.query.first()
        unidad = UnidadOrganizativa.query.first()
        ciudad = Ciudad.query.first()

        inserted_count = 0
        for idx, s in enumerate(DEBUG_STUDENTS_DATA):
            existente = Persona.query.filter(
                (Persona.numero_unico == s["nup"]) | (Persona.cedula == s["cedula"])
            ).first()

            if not existente:
                fixed_persona_id = f"00000000-0000-4000-b000-{(idx + 1):012d}"
                persona = Persona(
                    id=fixed_persona_id,
                    numero_unico=s["nup"],
                    cedula=s["cedula"],
                    nombres_apellidos=s["nombres"],
                    sexo=s["sexo"],
                    ciudad_residencia_id=ciudad.id if ciudad else str(uuid.uuid4()),
                    ciudad_procedencia_id=ciudad.id if ciudad else str(uuid.uuid4()),
                    sede_id=sede.id if sede else str(uuid.uuid4())
                )
                db.session.add(persona)
                db.session.flush()

                estudiante = Estudiante(
                    persona_id=persona.id,
                    carnet_estudiante=s["carnet"],
                    area_conocimiento_id=unidad.id if unidad else str(uuid.uuid4()),
                    carrera=s["carrera"],
                    ano_academico=s["ano"],
                    grupo=s["grupo"],
                    turno=s["turno"]
                )
                db.session.add(estudiante)
                inserted_count += 1

        db.session.commit()
        print(f"[OK] {inserted_count} estudiantes de prueba agregados exitosamente al padrón.")

        print("\n" + "=" * 95)
        print(" ESTUDIANTES DISPONIBLES PARA PRUEBAS Y ESCANEO (3nStar Sc050 / BÚSQUEDA)")
        print("=" * 95)
        print(f"{'CÉDULA':<18} | {'#NUP':<14} | {'CARNÉ':<11} | {'CARRERA (GRUPO)':<26} | NOMBRES Y APELLIDOS")
        print("-" * 95)
        
        personas = Persona.query.join(Estudiante).all()
        for p in personas:
            est = p.estudiante
            carrera_grp = f"{est.carrera[:17]} ({est.grupo})"
            print(f"{p.cedula:<18} | {p.numero_unico:<14} | {est.carnet_estudiante:<11} | {carrera_grp:<26} | {p.nombres_apellidos}")
        print("=" * 95)

if __name__ == "__main__":
    populate_test_students()
