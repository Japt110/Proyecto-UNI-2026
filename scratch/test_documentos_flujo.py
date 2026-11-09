"""
Script de verificación del ciclo completo de Documentos del Estudiante (CV, Récord Policial, Licencia de Conducir)
y visualización por parte del ofertante para ejercer su veredicto.
"""
import sys
import os
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database import db
from models.usuarios_auditoria import Usuario
from models.ofertas import OfertaPasantia, AplicacionOferta
from models.experiencias import Documento
from models.perfil_estudiante import Estudiante

app = create_app()

def run_tests():
    with app.test_client() as client:
        print("\n" + "="*70)
        print("VERIFICACIÓN DE FLUJO DE DOCUMENTOS Y VEREDICTO DE OFERTANTE")
        print("="*70)

        with app.app_context():
            estudiante_user = Usuario.query.filter_by(rol="Estudiante").first()
            admin_user = Usuario.query.filter_by(rol="Administrador").first()

            assert estudiante_user is not None, "Debe existir un estudiante"
            assert admin_user is not None, "Debe existir un administrador"

            estudiante_id = estudiante_user.id_usuario
            id_est = estudiante_user.id_estudiante
            admin_id = admin_user.id_usuario

        print(f"[*] Estudiante evaluado: ID={id_est}, Usuario ID={estudiante_id}")
        print(f"[*] Administrador / Ofertante: ID={admin_id}")

        # -------------------------------------------------------------
        # 1. Estudiante sube documentos a su persona (CV, Récord, Licencia)
        # -------------------------------------------------------------
        print("\n--- [1] Carga de Documentos Ligados a la Persona del Estudiante ---")
        with client.session_transaction() as sess:
            sess["user_id"] = estudiante_id
            sess["user_role"] = "Estudiante"

        # 1.1 Subir CV (Curriculum Vitae)
        cv_data = {
            "tipo_documento": "CV",
            "archivo": (io.BytesIO(b"%PDF-1.4 Mock CV de Carlos Mendoza - Ingeniero de Software"), "CV_Carlos_Mendoza_2026.pdf")
        }
        res = client.post("/api/estudiantes/documentos", data=cv_data, content_type="multipart/form-data")
        assert res.status_code == 201, f"Error al subir CV: {res.get_json()}"
        doc_cv = res.get_json()["documento"]
        doc_cv_id = doc_cv["id_documento"]
        print(f" [OK] CV subido: ID={doc_cv_id}, Archivo='{doc_cv['nombre_original']}', Tipo={doc_cv['tipo_documento']}")

        # 1.2 Subir Récord Policial
        record_data = {
            "tipo_documento": "Record_Policial",
            "archivo": (io.BytesIO(b"%PDF-1.4 Mock Certificado de Conducta Policia Nacional"), "Record_Policial_Nacional.pdf")
        }
        res = client.post("/api/estudiantes/documentos", data=record_data, content_type="multipart/form-data")
        assert res.status_code == 201
        doc_record = res.get_json()["documento"]
        doc_record_id = doc_record["id_documento"]
        print(f" [OK] Récord Policial subido: ID={doc_record_id}, Archivo='{doc_record['nombre_original']}'")

        # 1.3 Subir Licencia de Conducir (formato base64 o multipart)
        licencia_data = {
            "tipo_documento": "Licencia_Conducir",
            "archivo": (io.BytesIO(b"MOCK IMAGE BYTES DE LICENCIA CATEGORIA 1 2 3"), "Licencia_Conducir_Cat3.png")
        }
        res = client.post("/api/estudiantes/documentos", data=licencia_data, content_type="multipart/form-data")
        assert res.status_code == 201
        doc_licencia = res.get_json()["documento"]
        doc_licencia_id = doc_licencia["id_documento"]
        print(f" [OK] Licencia de Conducir subida: ID={doc_licencia_id}, Archivo='{doc_licencia['nombre_original']}'")

        # 1.4 Verificar en base de datos SQLAlchemy (tabla documentos)
        with app.app_context():
            docs_db = Documento.query.filter_by(id_estudiante=id_est).all()
            assert len(docs_db) >= 3, "Deben existir al menos 3 documentos en la tabla documentos"
            tipos_guardados = {d.tipo_documento for d in docs_db}
            assert "CV" in tipos_guardados
            assert "Record_Policial" in tipos_guardados
            assert "Licencia_Conducir" in tipos_guardados
            print(f" [OK] Persistencia en tabla 'documentos' verificada. Total documentos: {len(docs_db)}")

        # 1.5 Consultar documentos del estudiante (GET /api/estudiantes/documentos)
        res = client.get("/api/estudiantes/documentos")
        assert res.status_code == 200
        docs_api = res.get_json()["documentos"]
        assert len(docs_api) >= 3
        print(" [OK] GET /api/estudiantes/documentos retorna listado completo")

        # -------------------------------------------------------------
        # 2. Estudiante postula a una oferta de pasantía
        # -------------------------------------------------------------
        print("\n--- [2] Postulación a Pasantía con Expediente Completo ---")
        # Obtener o crear una oferta activa
        with app.app_context():
            oferta = OfertaPasantia.query.filter_by(estado="Activo").first()
            if not oferta:
                oferta = OfertaPasantia(
                    titulo="Pasantía de Prueba con Documentación",
                    tipo="Académica",
                    modalidad="Presencial",
                    duracion="160H",
                    experiencia="Sin experiencia",
                    sector="Tecnología",
                    ciudad="Managua",
                    cupos=2,
                    estado="Activo",
                    descripcion="Oferta para evaluar candidatos con documentos."
                )
                db.session.add(oferta)
                db.session.commit()
            id_oferta = oferta.id_oferta

        # Postular estudiante (eliminar si ya existía para prueba limpia)
        with app.app_context():
            AplicacionOferta.query.filter_by(id_oferta=id_oferta, id_estudiante=id_est).delete()
            db.session.commit()

        res = client.post(f"/api/pasantias/{id_oferta}/aplicar", json={"mensaje": "Postulación con CV y Récord adjuntos."})
        assert res.status_code == 201
        app_id = res.get_json()["aplicacion"]["id_aplicacion"]
        print(f" [OK] Postulación ID={app_id} enviada para Oferta ID={id_oferta}")

        # -------------------------------------------------------------
        # 3. Ofertante visualiza datos del candidato Y sus documentos
        # -------------------------------------------------------------
        print("\n--- [3] Ofertante / Empresa Evalúa Candidatos y Documentos (CU-07) ---")
        with client.session_transaction() as sess:
            sess["user_id"] = admin_id
            sess["user_role"] = "Administrador"

        res = client.get(f"/api/pasantias/{id_oferta}/aplicaciones")
        assert res.status_code == 200
        data_apps = res.get_json()
        assert data_apps["success"] is True

        postulaciones = data_apps["postulaciones"]
        postulacion_estudiante = next((p for p in postulaciones if p["id_estudiante"] == id_est), None)
        assert postulacion_estudiante is not None, "La postulación del estudiante debe estar en la lista"

        candidato = postulacion_estudiante.get("candidato")
        assert candidato is not None, "Debe incluir la información detallada del candidato"
        print(f" [OK] Candidato: {candidato['nombre_completo']}, CUP: {candidato['cup']}, Carrera: {candidato['carrera']}")

        docs_candidato = candidato.get("documentos", [])
        assert len(docs_candidato) >= 3, f"El ofertante debe poder ver los documentos del estudiante (obtenidos {len(docs_candidato)})"
        print(f" [OK] Documentos del candidato accesibles para veredicto ({len(docs_candidato)} docs):")
        for d in docs_candidato:
            print(f"      - {d['tipo_documento']}: '{d['nombre_original']}' -> Ruta: {d['ruta_archivo']}")

        # -------------------------------------------------------------
        # 4. Ofertante emite veredicto (Aceptado)
        # -------------------------------------------------------------
        print("\n--- [4] Emisión de Veredicto por el Ofertante ---")
        res = client.put(f"/api/pasantias/aplicaciones/{app_id}/estado", json={"nuevo_estado": "Aceptado"})
        assert res.status_code == 200
        print(" [OK] Veredicto 'Aceptado' emitido exitosamente con formalización atómica")

        with app.app_context():
            app_record = AplicacionOferta.query.get(app_id)
            assert app_record.estado == "Aceptado"

        # -------------------------------------------------------------
        # 5. Estudiante elimina un documento (limpieza de prueba)
        # -------------------------------------------------------------
        print("\n--- [5] Eliminación de Documento por el Estudiante ---")
        with client.session_transaction() as sess:
            sess["user_id"] = estudiante_id
            sess["user_role"] = "Estudiante"

        res = client.delete(f"/api/estudiantes/documentos/{doc_licencia_id}")
        assert res.status_code == 200
        print(f" [OK] Documento Licencia ID={doc_licencia_id} eliminado de la base de datos")

        with app.app_context():
            assert Documento.query.get(doc_licencia_id) is None

        print("\n" + "="*70)
        print("¡TODAS LAS PRUEBAS DE CARGA DE DOCUMENTOS Y VEREDICTO PASARON (100%)!")
        print("="*70)

if __name__ == "__main__":
    run_tests()
