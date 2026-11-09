import json
from app import create_app
from database import db
from models.usuarios_auditoria import Usuario

app = create_app()

def test_admin_usuarios():
    with app.app_context():
        admin = Usuario.query.filter_by(rol="Administrador").first()
        student = Usuario.query.filter_by(rol="Estudiante").first()
        supervisor = Usuario.query.filter_by(rol="Supervisor").first()

        assert admin is not None, "Admin user must exist"
        assert student is not None, "Student user must exist"

        client = app.test_client()

        # 1. Anonymous access -> 401 Unauthorized
        res_anon = client.get("/api/admin/usuarios")
        assert res_anon.status_code == 401, f"Expected 401 for anonymous, got {res_anon.status_code}"
        print("PASS: Anonymous access blocked with 401.")

        # 2. Student access -> 403 Forbidden
        with client.session_transaction() as sess:
            sess["user_id"] = student.id_usuario
            sess["user_role"] = "Estudiante"

        res_stud = client.get("/api/admin/usuarios")
        assert res_stud.status_code == 403, f"Expected 403 for Student, got {res_stud.status_code}"
        print("PASS: Student access blocked with 403.")

        # Student accessing HTML view -> 403
        res_stud_html = client.get("/admin/usuarios")
        assert res_stud_html.status_code == 403, f"Expected 403 for Student HTML view, got {res_stud_html.status_code}"
        print("PASS: Student access to /admin/usuarios HTML view blocked with 403.")

        # 3. Admin access -> 200 OK
        with client.session_transaction() as sess:
            sess["user_id"] = admin.id_usuario
            sess["user_role"] = "Administrador"

        res_admin = client.get("/api/admin/usuarios")
        assert res_admin.status_code == 200, f"Expected 200 for Admin, got {res_admin.status_code}"
        data = res_admin.get_json()
        assert data["success"] is True
        assert "usuarios" in data
        assert data["total"] >= 1
        print(f"PASS: Admin access granted. Total users: {data['total']}.")

        # Admin accessing HTML view -> 200 OK
        res_admin_html = client.get("/admin/usuarios")
        assert res_admin_html.status_code == 200, f"Expected 200 for Admin HTML view, got {res_admin_html.status_code}"
        html = res_admin_html.get_data(as_text=True)
        assert "MÓDULO DE AUDITORÍA Y USUARIOS" in html
        assert "adminApp" in html
        print("PASS: Admin view /admin/usuarios loads with 200 OK.")

        # 4. Pagination Test: 2 per page
        res_page1 = client.get("/api/admin/usuarios?pagina=1&por_pagina=2")
        d1 = res_page1.get_json()
        assert d1["pagina"] == 1
        assert d1["por_pagina"] == 2
        assert len(d1["usuarios"]) <= 2
        assert d1["paginas"] >= 1
        print(f"PASS: Pagination page 1 working (returned {len(d1['usuarios'])} users, {d1['paginas']} pages total).")

        res_page2 = client.get("/api/admin/usuarios?pagina=2&por_pagina=2")
        d2 = res_page2.get_json()
        assert d2["pagina"] == 2
        print(f"PASS: Pagination page 2 working.")

        # 5. Role Filter: Estudiante
        res_rol_est = client.get("/api/admin/usuarios?rol=Estudiante")
        d_est = res_rol_est.get_json()
        assert d_est["success"] is True
        for u in d_est["usuarios"]:
            assert u["rol"] == "Estudiante", f"Expected Estudiante, got {u['rol']}"
        print(f"PASS: Role filter 'Estudiante' returned {len(d_est['usuarios'])} students.")

        # 6. Role Filter: Supervisor
        res_rol_sup = client.get("/api/admin/usuarios?rol=Supervisor")
        d_sup = res_rol_sup.get_json()
        assert d_sup["success"] is True
        for u in d_sup["usuarios"]:
            assert u["rol"] == "Supervisor", f"Expected Supervisor, got {u['rol']}"
        print(f"PASS: Role filter 'Supervisor' returned {len(d_sup['usuarios'])} supervisors.")

        # 7. Username Filter: carlos.mendoza
        res_user_filter = client.get("/api/admin/usuarios?username=carlos.mendoza")
        d_user = res_user_filter.get_json()
        assert d_user["total"] == 1
        assert d_user["usuarios"][0]["nombre_usuario"] == "carlos.mendoza"
        print("PASS: Filter by username 'carlos.mendoza' returned exactly 1 matching user.")

        # 8. Name Filter: Roberto
        res_name_filter = client.get("/api/admin/usuarios?nombre=Roberto")
        d_name = res_name_filter.get_json()
        assert d_name["total"] >= 1
        assert "Roberto" in d_name["usuarios"][0]["nombre_completo"]
        print(f"PASS: Filter by personal name 'Roberto' returned: {d_name['usuarios'][0]['nombre_completo']}.")

        # 9. Global Search: 'BANPRO'
        res_search = client.get("/api/admin/usuarios?busqueda=banpro")
        d_search = res_search.get_json()
        assert d_search["total"] >= 1
        found_banpro = any("BANPRO" in str(u.get("detalles_actor", {}).get("empresa", "")) for u in d_search["usuarios"])
        assert found_banpro, "Search 'banpro' should find associated supervisor"
        print("PASS: Global search 'banpro' matched supervisor personification.")

        # 10. Self-deactivation prevention
        res_self = client.put(f"/api/admin/usuarios/{admin.id_usuario}/toggle-activo")
        assert res_self.status_code == 400
        assert "No puedes desactivar tu propia cuenta" in res_self.get_json()["message"]
        print("PASS: Prevention of self-deactivation verified.")

        # 11. Toggle active status on student
        current_status = student.activo
        res_toggle = client.put(f"/api/admin/usuarios/{student.id_usuario}/toggle-activo")
        assert res_toggle.status_code == 200
        d_tog = res_toggle.get_json()
        assert d_tog["activo"] == (not current_status)
        print(f"PASS: Toggled student active status from {current_status} to {d_tog['activo']}.")

        # Restore status
        client.put(f"/api/admin/usuarios/{student.id_usuario}/toggle-activo")

        # 12. Statistics endpoint
        res_stats = client.get("/api/admin/usuarios/estadisticas")
        assert res_stats.status_code == 200
        stats = res_stats.get_json()["estadisticas"]
        assert stats["total"] >= 1
        assert "Estudiante" in stats["por_rol"]
        print(f"PASS: Statistics endpoint verified (total: {stats['total']}, roles: {stats['por_rol']}).")

        print("\nALL ADMIN USER MANAGEMENT & FILTERING TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_admin_usuarios()
