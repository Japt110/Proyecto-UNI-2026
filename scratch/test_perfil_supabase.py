import os
import sys

# Agregar raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database import db
from models.usuarios_auditoria import Usuario
from models.perfil_estudiante import Estudiante, TelefonoEstudiante, DireccionEstudiante

def test_perfil():
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    with app.app_context():
        # 1. Probar con Estudiante
        print("=== 1. Prueba de Perfil con Estudiante (carlos.mendoza) ===")
        user = Usuario.query.filter_by(nombre_usuario="carlos.mendoza").first()
        assert user is not None, "Usuario carlos.mendoza no encontrado en Supabase"
        estudiante = Estudiante.query.get(user.id_estudiante)
        assert estudiante is not None, "Estudiante no vinculado"
        print(f"Estudiante actual en Supabase: {estudiante.nombre} {estudiante.apellido}, CUP: {estudiante.cup}")

        with client.session_transaction() as sess:
            sess.clear()
            sess["user_id"] = user.id_usuario
            sess["rol"] = user.rol
            sess["username"] = user.nombre_usuario

        # GET /perfil
        res = client.get("/perfil")
        assert res.status_code == 200, f"Error en GET /perfil: {res.status_code}"
        html = res.data.decode("utf-8")
        assert "Cargando ficha socio-académica" not in html, "El template contiene el mensaje de carga obsoleto!"
        assert estudiante.cup in html, "El CUP no fue pre-renderizado en el HTML"
        assert "EDITAR" in html, "El botón EDITAR no está en el HTML"
        print(" [OK] GET /perfil pre-renderiza instantáneamente los datos de Supabase sin pantallas de carga.")

        # PUT /api/pasantias/perfil (Edición de perfil)
        nuevo_nombre = "Carlos Eduardo"
        nuevo_apellido = "Mendoza Jarquín"
        nuevo_telefono = "8899-7711"
        nuevo_email = "carlos.mendoza.upd@est.uni.edu.ni"
        nueva_direccion = "Colonia Centroamérica, Módulo D-14"

        update_payload = {
            "nombre": nuevo_nombre,
            "apellido": nuevo_apellido,
            "telefono": nuevo_telefono,
            "correo": nuevo_email,
            "departamento": "Managua",
            "municipio": "Managua",
            "direccion": nueva_direccion,
            "has_2fa": True,
        }

        put_res = client.put("/api/pasantias/perfil", json=update_payload)
        assert put_res.status_code == 200, f"PUT /api/pasantias/perfil falló: {put_res.status_code} - {put_res.data}"
        json_data = put_res.get_json()
        assert json_data.get("success") is True, f"Respuesta no exitosa: {json_data}"
        print(f" [OK] PUT /api/pasantias/perfil respondió éxito: {json_data.get('message')}")

        # Comprobar directamente en Supabase
        db.session.expire_all()
        est_updated = Estudiante.query.get(estudiante.id_estudiante)
        usr_updated = Usuario.query.get(user.id_usuario)
        tel_updated = TelefonoEstudiante.query.filter_by(id_estudiante=estudiante.id_estudiante, es_principal=True).first()
        dir_updated = DireccionEstudiante.query.filter_by(id_estudiante=estudiante.id_estudiante, es_principal=True).first()

        assert est_updated.nombre == nuevo_nombre, f"Nombre no persistió: {est_updated.nombre}"
        assert est_updated.apellido == nuevo_apellido, f"Apellido no persistió: {est_updated.apellido}"
        assert usr_updated.email == nuevo_email, f"Email no persistió: {usr_updated.email}"
        assert usr_updated.has_2fa is True, f"has_2fa no persistió: {usr_updated.has_2fa}"
        assert tel_updated is not None and tel_updated.numero == nuevo_telefono, f"Teléfono no persistió: {tel_updated}"
        assert dir_updated is not None and dir_updated.direccion_domiciliar == nueva_direccion, f"Dirección no persistió: {dir_updated}"
        print(" [OK] Todos los cambios persistieron de forma verificable en Supabase PostgreSQL.")

        # Re-renderizar GET /perfil para confirmar que los nuevos datos se muestran
        res2 = client.get("/perfil")
        html2 = res2.data.decode("utf-8")
        assert nuevo_nombre in html2, "El nuevo nombre no aparece en /perfil"
        assert nuevo_telefono in html2, "El nuevo teléfono no aparece en /perfil"
        assert nueva_direccion in html2, "La nueva dirección no aparece en /perfil"
        print(" [OK] GET /perfil refleja inmediatamente los datos actualizados.")

        # 2. Probar con Administrador (admin)
        print("\n=== 2. Prueba de Perfil con Administrador (admin) ===")
        admin_user = Usuario.query.filter_by(nombre_usuario="admin").first()
        assert admin_user is not None

        with client.session_transaction() as sess:
            sess.clear()
            sess["user_id"] = admin_user.id_usuario
            sess["rol"] = admin_user.rol
            sess["username"] = admin_user.nombre_usuario

        admin_res = client.get("/perfil")
        assert admin_res.status_code == 200
        admin_html = admin_res.data.decode("utf-8")
        assert "admin" in admin_html
        print(" [OK] GET /perfil para Administrador funciona correctamente.")

        admin_put = client.put("/api/pasantias/perfil", json={
            "nombre": "admin",
            "correo": "admin_audit@uni.edu.ni",
            "has_2fa": False,
        })
        assert admin_put.status_code == 200
        db.session.expire_all()
        admin_check = Usuario.query.get(admin_user.id_usuario)
        assert admin_check.email == "admin_audit@uni.edu.ni"
        assert admin_check.has_2fa is False
        print(" [OK] Edición de perfil de Administrador persistió en Supabase.")

        print("\n=== ¡TODAS LAS PRUEBAS DE PERFIL Y CONEXIÓN SUPABASE PASARON CON ÉXITO! ===")

if __name__ == "__main__":
    test_perfil()
