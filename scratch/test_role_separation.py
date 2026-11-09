"""
Script de verificación de separación estricta de roles (RBAC)
Comprueba el acceso a endpoints comunes, exclusivos de administradores y exclusivos de estudiantes.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database import db
from models.usuarios_auditoria import Usuario

app = create_app()

def run_tests():
    with app.test_client() as client:
        print("\n" + "="*70)
        print("VERIFICACIÓN DE SEPARACIÓN ESTRICTA DE ROLES (RBAC)")
        print("="*70)

        # -------------------------------------------------------------
        # 0. Obtener IDs de usuarios para simulación
        # -------------------------------------------------------------
        with app.app_context():
            admin_user = Usuario.query.filter_by(rol="Administrador").first()
            estudiante_user = Usuario.query.filter_by(rol="Estudiante").first()
            supervisor_user = Usuario.query.filter_by(rol="Supervisor").first()

            assert admin_user is not None, "Debe existir un Administrador en la BD"
            assert estudiante_user is not None, "Debe existir un Estudiante en la BD"

            admin_id = admin_user.id_usuario
            admin_role = admin_user.rol
            estudiante_id = estudiante_user.id_usuario
            estudiante_role = estudiante_user.rol
            supervisor_id = supervisor_user.id_usuario if supervisor_user else None
            supervisor_role = supervisor_user.rol if supervisor_user else "Supervisor"

        print(f"[*] Admin de prueba: ID={admin_id}, Rol={admin_role}")
        print(f"[*] Estudiante de prueba: ID={estudiante_id}, Rol={estudiante_role}")

        # -------------------------------------------------------------
        # 1. PRUEBAS SIN AUTENTICAR (Debe dar 401 o 302 a /login)
        # -------------------------------------------------------------
        print("\n--- [1] Endpoints protegidos sin autenticar ---")
        res = client.get("/api/pasantias")
        assert res.status_code == 401, f"Esperado 401, obtenido {res.status_code}"
        print(" [OK] GET /api/pasantias sin sesión -> 401 Unauthorized")

        res = client.get("/")
        assert res.status_code == 302 and "/login" in res.headers.get("Location", ""), "Debe redirigir a /login"
        print(" [OK] GET / (HTML) sin sesión -> 302 Redirect a /login")

        # -------------------------------------------------------------
        # 2. PRUEBAS CON ROL: ESTUDIANTE
        # -------------------------------------------------------------
        print("\n--- [2] Evaluando permisos de rol ESTUDIANTE ---")
        with client.session_transaction() as sess:
            sess["user_id"] = estudiante_id
            sess["user_role"] = estudiante_role

        # 2.1 Endpoints comunes (Permitido)
        res = client.get("/api/pasantias")
        assert res.status_code == 200, f"Estudiante debe acceder a /api/pasantias (obtenido {res.status_code})"
        print(" [OK] Estudiante -> GET /api/pasantias (Común): 200 OK")

        res = client.get("/api/catalogos")
        assert res.status_code == 200, f"Estudiante debe acceder a /api/catalogos (obtenido {res.status_code})"
        print(" [OK] Estudiante -> GET /api/catalogos (Común): 200 OK")

        res = client.get("/")
        assert res.status_code == 200, f"Estudiante debe acceder a vista / (obtenido {res.status_code})"
        print(" [OK] Estudiante -> GET / (Vista Común): 200 OK")

        # 2.2 Endpoints exclusivos de estudiante (Permitido)
        res = client.get("/api/pasantias/mis-aplicaciones")
        assert res.status_code == 200, f"Estudiante debe acceder a /api/pasantias/mis-aplicaciones (obtenido {res.status_code})"
        print(" [OK] Estudiante -> GET /api/pasantias/mis-aplicaciones (Exclusivo Estudiante): 200 OK")

        # 2.3 Endpoints exclusivos de Administrador (BLOQUEADO 403)
        res = client.put("/api/empresas/1/aprobar")
        assert res.status_code == 403, f"Estudiante NO debe aprobar empresas (obtenido {res.status_code})"
        print(" [OK] Estudiante -> PUT /api/empresas/1/aprobar (Exclusivo Admin): 403 Forbidden BLOQUEADO")

        res = client.put("/api/empresas/1/rechazar")
        assert res.status_code == 403, f"Estudiante NO debe rechazar empresas (obtenido {res.status_code})"
        print(" [OK] Estudiante -> PUT /api/empresas/1/rechazar (Exclusivo Admin): 403 Forbidden BLOQUEADO")

        res = client.get("/api/vinculacion/metricas")
        assert res.status_code == 403, f"Estudiante NO debe ver métricas de vinculación (obtenido {res.status_code})"
        print(" [OK] Estudiante -> GET /api/vinculacion/metricas (Exclusivo Admin): 403 Forbidden BLOQUEADO")

        res = client.get("/api/stats/globales")
        assert res.status_code == 403, f"Estudiante NO debe ver estadísticas globales de rectoría (obtenido {res.status_code})"
        print(" [OK] Estudiante -> GET /api/stats/globales (Exclusivo Admin): 403 Forbidden BLOQUEADO")

        # 2.4 Endpoints de Empresa / Admin (BLOQUEADO 403 para Estudiante)
        res = client.post("/api/pasantias", json={"titulo": "Test"})
        assert res.status_code == 403, f"Estudiante NO debe crear ofertas (obtenido {res.status_code})"
        print(" [OK] Estudiante -> POST /api/pasantias (Empresa/Admin): 403 Forbidden BLOQUEADO")

        res = client.get("/api/pasantias/1/aplicaciones")
        assert res.status_code == 403, f"Estudiante NO debe auditar candidatos de oferta (obtenido {res.status_code})"
        print(" [OK] Estudiante -> GET /api/pasantias/1/aplicaciones (Empresa/Admin): 403 Forbidden BLOQUEADO")

        # -------------------------------------------------------------
        # 3. PRUEBAS CON ROL: ADMINISTRADOR
        # -------------------------------------------------------------
        print("\n--- [3] Evaluando permisos de rol ADMINISTRADOR ---")
        with client.session_transaction() as sess:
            sess["user_id"] = admin_id
            sess["user_role"] = admin_role

        # 3.1 Endpoints comunes (Permitido)
        res = client.get("/api/pasantias")
        assert res.status_code == 200, f"Admin debe acceder a /api/pasantias (obtenido {res.status_code})"
        print(" [OK] Administrador -> GET /api/pasantias (Común): 200 OK")

        res = client.get("/")
        assert res.status_code == 200, f"Admin debe acceder a vista / (obtenido {res.status_code})"
        print(" [OK] Administrador -> GET / (Vista Común): 200 OK")

        # 3.2 Endpoints exclusivos de Administrador (Permitido)
        res = client.get("/api/vinculacion/metricas")
        assert res.status_code == 200, f"Admin debe acceder a métricas (obtenido {res.status_code})"
        print(" [OK] Administrador -> GET /api/vinculacion/metricas (Exclusivo Admin): 200 OK")

        # 3.3 Endpoints exclusivos de ESTUDIANTE (BLOQUEADO 403 para Administrador)
        res = client.post("/api/pasantias/1/aplicar", json={"motivo_postulacion": "Admin intentando postularse"})
        assert res.status_code == 403, f"Admin NO debe postularse a pasantías (obtenido {res.status_code})"
        print(" [OK] Administrador -> POST /api/pasantias/1/aplicar (Exclusivo Estudiante): 403 Forbidden BLOQUEADO")

        res = client.get("/api/pasantias/mis-aplicaciones")
        assert res.status_code == 403, f"Admin NO debe consultar postulaciones de estudiante (obtenido {res.status_code})"
        print(" [OK] Administrador -> GET /api/pasantias/mis-aplicaciones (Exclusivo Estudiante): 403 Forbidden BLOQUEADO")

        print("\n" + "="*70)
        print("¡TODAS LAS PRUEBAS DE SEPARACIÓN DE ROLES PASARON EXITOSAMENTE (100%)!")
        print("="*70)

if __name__ == "__main__":
    run_tests()
