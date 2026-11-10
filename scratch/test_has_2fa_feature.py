import json
from app import create_app
from database import db
from models.usuarios_auditoria import Usuario, AuditoriaCambios

app = create_app()

def test_has_2fa_flow():
    with app.app_context():
        # Get test users
        admin = Usuario.query.filter_by(rol="Administrador").first()
        student = Usuario.query.filter_by(rol="Estudiante").first()

        assert admin is not None
        assert student is not None

        # Ensure default is False
        student.has_2fa = False
        admin.has_2fa = False
        db.session.commit()

        client = app.test_client()

        # -------------------------------------------------------------
        # TEST 1: Default Login when has_2fa is False -> Direct Login (NO 2FA)
        # -------------------------------------------------------------
        res_login_direct = client.post(
            "/api/auth/login",
            json={"identifier": "carlos.mendoza", "password": "estudiante123"}
        )
        assert res_login_direct.status_code == 200
        d_direct = res_login_direct.get_json()
        assert d_direct["success"] is True
        assert d_direct["requires_2fa"] is False, "Expected requires_2fa to be False when has_2fa=False"
        assert "token" in d_direct or "session_token" in d_direct
        print("PASS: Login with has_2fa=False logged in directly without requiring 2FA OTP.")

        # -------------------------------------------------------------
        # TEST 2: Activate 2FA via /api/auth/toggle-2fa
        # -------------------------------------------------------------
        with client.session_transaction() as sess:
            sess["user_id"] = student.id_usuario
            sess["user_role"] = "Estudiante"

        res_toggle_on = client.put("/api/auth/toggle-2fa", json={"has_2fa": True})
        assert res_toggle_on.status_code == 200
        d_tog_on = res_toggle_on.get_json()
        assert d_tog_on["has_2fa"] is True
        
        # Verify in DB
        db.session.refresh(student)
        assert student.has_2fa is True
        print("PASS: User activated 2FA via /api/auth/toggle-2fa.")

        # -------------------------------------------------------------
        # TEST 3: Login when has_2fa is True -> Must Require 2FA OTP
        # -------------------------------------------------------------
        res_login_2fa = client.post(
            "/api/auth/login",
            json={"identifier": "carlos.mendoza", "password": "estudiante123"}
        )
        assert res_login_2fa.status_code == 200
        d_2fa = res_login_2fa.get_json()
        assert d_2fa["success"] is True
        assert d_2fa["requires_2fa"] is True, "Expected requires_2fa to be True when has_2fa=True"
        assert "email_masked" in d_2fa
        print("PASS: Login with has_2fa=True triggered 2FA challenge.")

        # -------------------------------------------------------------
        # TEST 4: Deactivate 2FA via Profile update /api/pasantias/perfil
        # -------------------------------------------------------------
        with client.session_transaction() as sess:
            sess.clear()
            sess["user_id"] = student.id_usuario
            sess["user_role"] = "Estudiante"

        res_perfil_update = client.put(
            "/api/pasantias/perfil",
            json={"has_2fa": False, "nombre": "Carlos Alberto"}
        )
        assert res_perfil_update.status_code == 200, f"Error: {res_perfil_update.get_data(as_text=True)}"
        db.session.refresh(student)
        assert student.has_2fa is False
        print("PASS: Deactivated 2FA via profile update /api/pasantias/perfil.")

        # -------------------------------------------------------------
        # TEST 5: Verify /perfil view renders 2FA checkbox
        # -------------------------------------------------------------
        res_perfil_html = client.get("/perfil")
        assert res_perfil_html.status_code == 200
        html = res_perfil_html.get_data(as_text=True)
        assert 'id="perfil-has-2fa"' in html, "Checkbox perfil-has-2fa missing in /perfil"
        assert "Seguridad y Verificación en Dos Pasos" in html
        print("PASS: /perfil pre-rendered 2FA checkbox in user configuration.")

        # -------------------------------------------------------------
        # TEST 6: Admin toggling 2FA for a user via /api/admin/usuarios/<id>/toggle-2fa
        # -------------------------------------------------------------
        with client.session_transaction() as sess:
            sess["user_id"] = admin.id_usuario
            sess["user_role"] = "Administrador"

        res_admin_tog = client.put(f"/api/admin/usuarios/{student.id_usuario}/toggle-2fa", json={"has_2fa": True})
        assert res_admin_tog.status_code == 200
        d_adm = res_admin_tog.get_json()
        assert d_adm["has_2fa"] is True
        db.session.refresh(student)
        assert student.has_2fa is True

        # Check audit log
        audit = AuditoriaCambios.query.filter_by(
            tabla_afectada="usuarios",
            registro_id=student.id_usuario
        ).order_by(AuditoriaCambios.id_auditoria.desc()).first()
        assert audit is not None
        assert "has_2fa" in audit.columnas_modificadas
        print("PASS: Admin toggled 2FA with forensic audit tracking.")

        # Admin view HTML check
        res_admin_html = client.get("/admin/usuarios")
        assert res_admin_html.status_code == 200
        assert "modal-user-has-2fa" in res_admin_html.get_data(as_text=True)
        print("PASS: /admin/usuarios includes 2FA table column and detail modal controls.")

        # Clean state: set student has_2fa back to False
        student.has_2fa = False
        db.session.commit()

        print("\nALL HAS_2FA DATABASE, API, AND CONFIGURATION TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_has_2fa_flow()
