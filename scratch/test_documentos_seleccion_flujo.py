import sys
import io
import json
from app import create_app
from database import db
from models.usuarios_auditoria import Usuario
from models.catalogos import Carrera
from models.perfil_estudiante import Estudiante, Matricula
from models.actores_externos import EntidadReceptora
from models.ofertas import OfertaPasantia, AplicacionOferta
from models.experiencias import Documento

app = create_app()

def run_tests():
    with app.app_context():
        student_user = Usuario.query.filter_by(id_usuario=2).first()
        estudiante = Estudiante.query.filter_by(id_estudiante=student_user.id_estudiante).first()
        admin_user = Usuario.query.filter_by(rol="Administrador").first()

        # Ensure active matricula and 4th year for student
        mat = Matricula.query.filter_by(id_estudiante=estudiante.id_estudiante).first()
        if not mat:
            mat = Matricula(
                id_estudiante=estudiante.id_estudiante,
                periodo_academico="2026-I",
                anio_academico=4,
                estado="Activa"
            )
            db.session.add(mat)
            db.session.flush()
        else:
            mat.estado = "Activa"
            mat.anio_academico = 4

        # Clean prior test docs for clean test run
        Documento.query.filter_by(id_estudiante=estudiante.id_estudiante).delete()
        db.session.commit()

        # Find or create offer
        oferta = OfertaPasantia.query.first()
        if not oferta:
            empresa = EntidadReceptora.query.first()
            oferta = OfertaPasantia(
                id_entidad=empresa.id_entidad if empresa else None,
                titulo="Pasantía Test Docs",
                modalidad="Presencial",
                duracion_horas=160,
                nivel_experiencia="Junior",
                cupos_disponibles=2,
                descripcion="Prueba para documentos compartidos",
                estado="Activa"
            )
            db.session.add(oferta)
            db.session.flush()

        # Clean prior applications
        AplicacionOferta.query.filter_by(id_oferta=oferta.id_oferta, id_estudiante=estudiante.id_estudiante).delete()
        db.session.commit()

        client = app.test_client()

        # 1. Login as Student
        with client.session_transaction() as sess:
            sess["user_id"] = student_user.id_usuario
            sess["user_role"] = "Estudiante"
            sess["_fresh"] = True

        # 2. Check /perfil pre-rendered instant loading
        res_perfil = client.get("/perfil")
        assert res_perfil.status_code == 200, f"Expected 200, got {res_perfil.status_code}"
        html = res_perfil.get_data(as_text=True)
        assert "perfil-loading" not in html, "Old loading spinner found in /perfil!"
        assert "Carlos" in html, "Student name not pre-rendered in /perfil"
        assert 'id="perfil-documentos-seccion"' in html, "Document section not shown for student"
        print("PASS: /perfil instant server-side pre-render verified.")

        # 3. Upload Document 1 (CV)
        data_cv = {
            "tipo_documento": "CV",
            "archivo": (io.BytesIO(b"%PDF-1.4 Mock CV File Content"), "mi_cv_2026.pdf")
        }
        res_up1 = client.post("/api/estudiantes/documentos", data=data_cv, content_type="multipart/form-data")
        assert res_up1.status_code == 201, f"Failed uploading CV: {res_up1.get_data(as_text=True)}"
        doc1_data = res_up1.get_json()["documento"]
        doc1_id = doc1_data["id"]
        print(f"PASS: Uploaded CV with doc ID {doc1_id}")

        # Upload Document 2 (Licencia de Conducir)
        data_lic = {
            "tipo_documento": "Licencia_Conducir",
            "archivo": (io.BytesIO(b"MOCK IMAGE LICENCIA CONTENT"), "licencia_cat3.png")
        }
        res_up2 = client.post("/api/estudiantes/documentos", data=data_lic, content_type="multipart/form-data")
        assert res_up2.status_code == 201, f"Failed uploading Licencia: {res_up2.get_data(as_text=True)}"
        doc2_data = res_up2.get_json()["documento"]
        doc2_id = doc2_data["id"]
        print(f"PASS: Uploaded Licencia_Conducir with doc ID {doc2_id}")

        # 4. Attempt upload as non-student (Admin) -> Must return 403 Forbidden
        with client.session_transaction() as sess:
            sess["user_id"] = admin_user.id_usuario
            sess["user_role"] = "Administrador"

        data_admin = {
            "tipo_documento": "CV",
            "archivo": (io.BytesIO(b"%PDF-1.4 Admin File"), "admin_doc.pdf")
        }
        res_admin_up = client.post("/api/estudiantes/documentos", data=data_admin, content_type="multipart/form-data")
        assert res_admin_up.status_code == 403, f"Expected 403 Forbidden for non-student, got {res_admin_up.status_code}"
        print("PASS: Non-student document upload blocked with 403 Forbidden.")

        # 5. Clean prior test application if exists
        AplicacionOferta.query.filter_by(id_oferta=oferta.id_oferta, id_estudiante=estudiante.id_estudiante).delete()
        db.session.commit()

        # 6. Apply to internship as Student with SELECTIVE documents: ONLY share doc1 (CV), NOT doc2 (Licencia)
        with client.session_transaction() as sess:
            sess["user_id"] = student_user.id_usuario
            sess["user_role"] = "Estudiante"

        res_aplicar = client.post(
            f"/api/pasantias/{oferta.id_oferta}/aplicar",
            json={
                "motivo_postulacion": "Deseo aplicar compartiendo exclusivamente mi CV.",
                "documentos_compartidos": [doc1_id]
            }
        )
        assert res_aplicar.status_code == 201, f"Expected 201 Created, got {res_aplicar.status_code}: {res_aplicar.get_data(as_text=True)}"
        print("PASS: Application submitted with selective document list [CV].")

        # 7. As Company / Admin, view candidates for this offer
        with client.session_transaction() as sess:
            sess["user_id"] = admin_user.id_usuario
            sess["user_role"] = "Administrador"

        res_candidatos = client.get(f"/api/pasantias/{oferta.id_oferta}/aplicaciones")
        assert res_candidatos.status_code == 200, f"Error getting candidates: {res_candidatos.status_code}"
        cands_json = res_candidatos.get_json()
        assert cands_json["success"] is True

        app_item = next((a for a in cands_json["aplicaciones"] if a["candidato"]["id_estudiante"] == estudiante.id_estudiante), None)
        assert app_item is not None, "Application not found in candidates list"
        
        shared_docs = app_item["candidato"]["documentos"]
        shared_ids = [d["id"] for d in shared_docs]
        print(f"Candidate's visible documents to employer: {shared_ids}")
        assert doc1_id in shared_ids, "Authorized CV not visible to employer"
        assert doc2_id not in shared_ids, "UNAUTHORIZED Licencia_Conducir was leaked to employer!"
        print("PASS: Selective document privacy strictly enforced! Only checked documents are exposed to company.")

        print("\nALL INTEGRATION AND USER REQUIREMENT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
