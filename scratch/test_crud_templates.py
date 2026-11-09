"""
Verificación de Conexión CRUD Real con Base de Datos SQLAlchemy y Eliminación de Plantillas Visuales Obsoletas.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database import db
from models.usuarios_auditoria import Usuario
from models.ofertas import OfertaPasantia, AplicacionOferta
from models.perfil_estudiante import Estudiante, Matricula, TelefonoEstudiante, DireccionEstudiante
from models.experiencias import Experiencia, Pasantia

app = create_app()

def run_tests():
    with app.test_client() as client:
        print("\n" + "="*70)
        print("VERIFICACIÓN DE LIMPIEZA DE PLANTILLAS Y CRUD REAL CON ALCHEMY")
        print("="*70)

        # -------------------------------------------------------------
        # 1. Comprobar que las plantillas visuales obsoletas fueron eliminadas
        # -------------------------------------------------------------
        print("\n--- [1] Verificación de Eliminación de Plantillas Obsoletas ---")
        templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
        obsolete_templates = [
            "asistencia.html",
            "crear-actividad.html",
            "detalle-actividad.html",
            "rector.html",
            "usuarios.html"
        ]
        for t in obsolete_templates:
            exists = os.path.exists(os.path.join(templates_dir, t))
            assert not exists, f"La plantilla obsoleta {t} todavía existe en templates/"
            print(f" [OK] {t} eliminado de templates/")

        active_templates = [f for f in os.listdir(templates_dir) if f.endswith(".html")]
        print(f" [*] Plantillas activas en el sistema: {active_templates}")
        assert set(active_templates) == {"index.html", "login.html", "perfil.html"}

        # -------------------------------------------------------------
        # 2. CRUD Real de Ofertas de Pasantía en SQLAlchemy (Admin/Empresa)
        # -------------------------------------------------------------
        print("\n--- [2] Verificación de CRUD Real de Ofertas (SQLAlchemy) ---")
        with app.app_context():
            admin = Usuario.query.filter_by(rol="Administrador").first()
            assert admin is not None
            admin_id = admin.id_usuario
            admin_rol = admin.rol

        with client.session_transaction() as sess:
            sess["user_id"] = admin_id
            sess["user_role"] = admin_rol

        # 2.1 CREATE (POST /api/pasantias)
        oferta_payload = {
            "titulo": "Pasantía Automatizada en DevOps y Cloud UNI 2026",
            "tipo": "Profesional",
            "modalidad": "Híbrida",
            "duracion": "240H",
            "experiencia": "Junior",
            "sector": "Tecnología",
            "ciudad": "Managua",
            "cupos": 3,
            "remunerada": True,
            "requisitos": "Docker, Kubernetes, CI/CD",
            "descripcion": "Pasantía técnica de alto impacto para estudiantes de 4to o 5to año."
        }
        res = client.post("/api/pasantias", json=oferta_payload)
        assert res.status_code == 201, f"Error al crear oferta: {res.get_json()}"
        nueva_oferta = res.get_json()["pasantia"]
        oferta_id = nueva_oferta["id"]
        print(f" [OK] CREATE: Oferta ID={oferta_id} creada e insertada en SQLite")

        # Verificar en base de datos SQLAlchemy
        with app.app_context():
            db_oferta = OfertaPasantia.query.get(oferta_id)
            assert db_oferta is not None
            assert db_oferta.titulo == oferta_payload["titulo"]
            assert db_oferta.cupos == 3

        # 2.2 READ (GET /api/pasantias/<id> y GET /api/pasantias)
        res = client.get(f"/api/pasantias/{oferta_id}")
        assert res.status_code == 200
        assert res.get_json()["pasantia"]["titulo"] == oferta_payload["titulo"]
        print(f" [OK] READ: Consulta individual y filtro de oferta ID={oferta_id}")

        # 2.3 UPDATE (PUT /api/pasantias/<id>)
        update_payload = {
            "titulo": "Pasantía Automatizada en DevOps y Cloud UNI (ACTUALIZADA)",
            "cupos": 5
        }
        res = client.put(f"/api/pasantias/{oferta_id}", json=update_payload)
        assert res.status_code == 200
        with app.app_context():
            db_oferta = OfertaPasantia.query.get(oferta_id)
            assert db_oferta.titulo == update_payload["titulo"]
            assert db_oferta.cupos == 5
        print(f" [OK] UPDATE: Oferta ID={oferta_id} modificada en base de datos")

        # -------------------------------------------------------------
        # 3. Flujo Real de Postulación y Formalización (CU-03, CU-04, CU-07)
        # -------------------------------------------------------------
        print("\n--- [3] Verificación de Postulación y Transición Atómica (CU-03, CU-07) ---")
        with app.app_context():
            estudiante_user = Usuario.query.filter_by(rol="Estudiante").first()
            assert estudiante_user is not None
            estudiante_id = estudiante_user.id_usuario
            estudiante_rol = estudiante_user.rol
            id_est = estudiante_user.id_estudiante

        with client.session_transaction() as sess:
            sess["user_id"] = estudiante_id
            sess["user_role"] = estudiante_rol

        # 3.1 Estudiante postula a la oferta
        res = client.post(f"/api/pasantias/{oferta_id}/aplicar", json={"motivo_postulacion": "Interesado en DevOps"})
        assert res.status_code == 201, f"Error al postular: {res.get_json()}"
        app_id = res.get_json()["aplicacion"]["id_aplicacion"]
        print(f" [OK] POSTULARSE: Postulación ID={app_id} registrada en aplicaciones_oferta")

        # 3.2 Estudiante consulta mis aplicaciones
        res = client.get("/api/pasantias/mis-aplicaciones")
        assert res.status_code == 200
        apps_list = res.get_json()["aplicaciones"]
        assert any(a["id_aplicacion"] == app_id for a in apps_list)
        print(" [OK] MIS APLICACIONES: Estudiante visualiza su postulación activa")

        # 3.3 Admin evalúa y aprueba postulación -> Transición atómica a experiencias
        with client.session_transaction() as sess:
            sess["user_id"] = admin_id
            sess["user_role"] = admin_rol

        res = client.put(f"/api/pasantias/aplicaciones/{app_id}/estado", json={"nuevo_estado": "Aceptado"})
        assert res.status_code == 200, f"Error al aceptar postulación: {res.get_json()}"
        print(" [OK] ACEPTAR POSTULACIÓN: Transición atómica a Experiencia y Pasantía ejecutada")

        with app.app_context():
            app_record = AplicacionOferta.query.get(app_id)
            assert app_record.estado == "Aceptado"
            # Verificar experiencia generada
            exp = Experiencia.query.filter_by(id_estudiante=id_est).order_by(Experiencia.id_experiencia.desc()).first()
            assert exp is not None
            assert exp.tipo_experiencia in ("Pasantia", "Pasantía")
            pas = Pasantia.query.get(exp.id_experiencia)
            assert pas is not None
            print(f" [OK] ALCHEMY VALIDADO: Registro en 'experiencias' ID={exp.id_experiencia} y 'pasantias' persistido")

        # 2.4 DELETE (DELETE /api/pasantias/<id>)
        res = client.delete(f"/api/pasantias/{oferta_id}")
        assert res.status_code == 200
        with app.app_context():
            deleted_oferta = OfertaPasantia.query.get(oferta_id)
            assert deleted_oferta is None
        print(f" [OK] DELETE: Oferta ID={oferta_id} eliminada permanentemente de SQLite")

        # -------------------------------------------------------------
        # 4. CRUD de Ficha Socio-Académica / Perfil Estudiante (CU-01)
        # -------------------------------------------------------------
        print("\n--- [4] Verificación de CRUD de Perfil de Estudiante (CU-01) ---")
        with client.session_transaction() as sess:
            sess["user_id"] = estudiante_id
            sess["user_role"] = estudiante_rol

        # 4.1 READ (GET /api/pasantias/perfil)
        res = client.get("/api/pasantias/perfil")
        assert res.status_code == 200
        perfil_data = res.get_json()["perfil"]
        assert perfil_data["id_estudiante"] == id_est
        print(f" [OK] READ PERFIL: Nombre={perfil_data['nombre_completo']}, CUP={perfil_data['cup']}, Carrera={perfil_data['carrera']}")

        # 4.2 UPDATE (PUT /api/pasantias/perfil)
        update_perfil_payload = {
            "nombre": "Carlos Alberto",
            "apellido": "Mendoza Ruiz",
            "telefono": "8899-7766",
            "direccion": "Costado sur de UNI RUSB, Managua",
            "estado_civil": "Soltero(a)"
        }
        res = client.put("/api/pasantias/perfil", json=update_perfil_payload)
        assert res.status_code == 200

        with app.app_context():
            est_db = Estudiante.query.get(id_est)
            assert est_db.nombre == "Carlos Alberto"
            assert est_db.apellido == "Mendoza Ruiz"
            tel_db = TelefonoEstudiante.query.filter_by(id_estudiante=id_est, es_principal=True).first()
            assert tel_db is not None
            assert tel_db.numero == "8899-7766"
            dir_db = DireccionEstudiante.query.filter_by(id_estudiante=id_est, es_principal=True).first()
            assert dir_db is not None
            assert dir_db.direccion_domiciliar == "Costado sur de UNI RUSB, Managua"
        print(" [OK] UPDATE PERFIL: Datos socio-académicos actualizados directamente en SQLAlchemy")

        print("\n" + "="*70)
        print("¡TODAS LAS PRUEBAS DE LIMPIEZA DE PLANTILLAS Y CRUD ALCHEMY PASARON (100%)!")
        print("="*70)

if __name__ == "__main__":
    run_tests()
