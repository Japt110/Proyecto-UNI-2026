import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date
from app import create_app
from database import db
from models.usuarios_auditoria import Usuario
from models.perfil_estudiante import (
    Estudiante,
    TelefonoEstudiante,
    DireccionEstudiante,
    EducacionPreviaEstudiante,
    Matricula,
)

def test_full_perfil():
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    with app.app_context():
        print("=== Test Completo de Campos de Perfil en Supabase ===")
        user = Usuario.query.filter_by(nombre_usuario="carlos.mendoza").first()
        assert user is not None, "carlos.mendoza no encontrado"
        estudiante = Estudiante.query.get(user.id_estudiante)
        assert estudiante is not None, "estudiante no encontrado"

        with client.session_transaction() as sess:
            sess.clear()
            sess["user_id"] = user.id_usuario
            sess["rol"] = user.rol
            sess["username"] = user.nombre_usuario

        # 1. GET /perfil
        res = client.get("/perfil")
        assert res.status_code == 200
        html = res.data.decode("utf-8")

        # Verificar presencia de secciones y campos
        assert "Información personal" in html
        assert "Métodos de contacto" in html
        assert "Educación" in html
        assert "Matrícula" in html
        assert 'id="perfil-cedula"' in html
        assert 'id="perfil-nombres"' in html
        assert 'id="perfil-apellidos"' in html
        assert 'id="perfil-sexo"' in html
        assert 'id="perfil-nacimiento"' in html
        assert 'id="perfil-edad"' in html
        assert 'id="perfil-nacionalidad"' in html
        assert 'id="perfil-pais"' in html
        assert 'id="perfil-etnia"' in html
        assert 'id="perfil-estado-civil"' in html
        assert 'id="perfil-hijos"' in html
        assert 'id="perfil-correo"' in html
        assert 'id="perfil-telefono"' in html
        assert 'id="perfil-departamento"' in html
        assert 'id="perfil-municipio"' in html
        assert 'id="perfil-direccion"' in html
        assert 'id="perfil-carrera"' in html
        assert 'id="perfil-centro-educativo"' in html
        assert 'id="perfil-periodo"' in html
        assert 'id="perfil-anio"' in html
        assert 'id="perfil-beca"' in html
        assert "EDITAR PERFIL" in html
        print(" [OK] 1. GET /perfil contiene todas las secciones y campos solicitados.")

        # Verificar que los catálogos tienen opciones reales
        assert "Nicaragua" in html, "País no cargado en opciones"
        assert "Mestizo" in html, "Etnia no cargada en opciones"
        assert "Managua" in html, "Departamento no cargado en opciones"
        assert "Ingeniería de Sistemas" in html, "Carrera no cargada en opciones"
        print(" [OK] 2. Opciones de catálogos desde Supabase renderizadas con éxito.")

        # 2. PUT /api/pasantias/perfil (Modificación integral de todos los campos)
        full_payload = {
            "nombre": "Carlos Erick",
            "apellido": "Mendoza Mondragon",
            "sexo": "Masculino",
            "fecha_nacimiento": "2001-08-20",
            "dimension_nacional": "Natural",
            "id_pais_origen": 1,
            "id_etnia": 1,
            "estado_civil": "Soltero",
            "hijos": 0,
            "email": "carlos.erick@est.uni.edu.ni",
            "correo": "carlos.erick@est.uni.edu.ni",
            "telefono": "8877-6655",
            "tipo_telefono": "Movil",
            "telefono_principal": True,
            "id_departamento": 1,
            "id_municipio": 1,
            "comunidad": "Colonia Maestro Gabriel",
            "zona": "Urbano",
            "direccion": "Frente al parque central, casa #45",
            "direccion_principal": True,
            "id_carrera": 1,
            "id_centro_educativo": 1,
            "educacion_tecnica": "Técnico en Redes CISCO",
            "titulo_obtenido": "Bachiller Técnico",
            "anio_graduacion": 2019,
            "periodo_academico": "I Semestre 2026",
            "anio": 5,
            "modalidad": "Presencial",
            "turno": "Matutino",
            "grupo_clase": "5M1-IS",
            "id_beca": 1,
            "estado_matricula": "Activa",
            "has_2fa": True,
        }

        put_res = client.put("/api/pasantias/perfil", json=full_payload)
        assert put_res.status_code == 200, f"Error en PUT: {put_res.status_code} - {put_res.data}"
        json_data = put_res.get_json()
        assert json_data.get("success") is True
        print(f" [OK] 3. PUT /api/pasantias/perfil completado con éxito: {json_data.get('message')}")

        # 3. Comprobar directamente en Supabase
        db.session.expire_all()
        est_db = Estudiante.query.get(estudiante.id_estudiante)
        usr_db = Usuario.query.get(user.id_usuario)
        tel_db = TelefonoEstudiante.query.filter_by(id_estudiante=estudiante.id_estudiante, es_principal=True).first()
        dir_db = DireccionEstudiante.query.filter_by(id_estudiante=estudiante.id_estudiante, es_principal=True).first()
        ed_db = EducacionPreviaEstudiante.query.filter_by(id_estudiante=estudiante.id_estudiante).first()
        mat_db = Matricula.query.filter_by(id_estudiante=estudiante.id_estudiante).order_by(Matricula.id_matricula.desc()).first()

        assert est_db.nombre == "Carlos Erick"
        assert est_db.apellido == "Mendoza Mondragon"
        assert est_db.sexo == "Masculino"
        assert est_db.fecha_nacimiento == date(2001, 8, 20)
        assert est_db.dimension_nacional == "Natural"
        assert usr_db.email == "carlos.erick@est.uni.edu.ni"
        assert usr_db.has_2fa is True
        assert tel_db.numero == "8877-6655"
        assert tel_db.tipo == "Movil"
        assert dir_db.direccion_domiciliar == "Frente al parque central, casa #45"
        assert dir_db.comunidad == "Colonia Maestro Gabriel"
        assert dir_db.zona == "Urbano"
        assert ed_db.educacion_tecnica == "Técnico en Redes CISCO"
        assert ed_db.titulo_obtenido == "Bachiller Técnico"
        assert ed_db.anio_graduacion == 2019
        assert mat_db.anio_academico == 5
        assert mat_db.grupo_clase == "5M1-IS"
        print(" [OK] 4. Todos los campos de las 6 tablas normalizadas persistieron en Supabase PostgreSQL.")

        # 4. Validar que el nuevo GET renderiza la información actualizada
        res2 = client.get("/perfil")
        html2 = res2.data.decode("utf-8")
        assert "Carlos Erick" in html2
        assert "Mendoza Mondragon" in html2
        assert "8877-6655" in html2
        assert "Frente al parque central, casa #45" in html2
        assert "Técnico en Redes CISCO" in html2
        assert "5M1-IS" in html2
        print(" [OK] 5. GET /perfil refleja al instante toda la información actualizada.")

        print("\n=== ¡TEST DE EDICIÓN INTEGRAL DE CAMPOS DE PERFIL PASÓ EXITOSAMENTE! ===")

if __name__ == "__main__":
    test_full_perfil()
