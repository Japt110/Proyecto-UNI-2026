"""Registro, persistencia, autenticación y límites del rol Estudiante."""
import unittest
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app import create_app
from database import db
from models.base import Estudiante, Usuario


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {}, "SQLALCHEMY_BINDS": {},
            "SECRET_KEY": "test-only-registration", "RATE_LIMIT_ENABLED": False,
            "CACHE_TYPE": "SimpleCache", "SESSION_COOKIE_SECURE": False,
        })
        self.client = self.app.test_client()
        self.payload = {"nombres": "María José", "apellidos": "Pérez-García", "sexo": "Femenino",
                        "numero_unico": "TEST-2026-101", "cedula": "001-120503-1004A",
                        "email": "test.registration@outlook.com", "password": "Testing123!"}

    def register(self, payload=None):
        csrf = self.client.get("/api/auth/registration-csrf").json["csrf_token"]
        return self.client.post("/api/auth/register", json=self.payload if payload is None else payload,
                                headers={"X-CSRF-Token": csrf})

    def assert_empty(self):
        with self.app.app_context():
            self.assertEqual([Estudiante.query.count(), Usuario.query.count()], [0, 0])

    def test_persists_all_fields_links_and_hash_in_one_account(self):
        result = self.register()
        self.assertEqual(result.status_code, 201)
        self.assertNotIn("password", result.json)
        with self.app.app_context():
            student, user = Estudiante.query.one(), Usuario.query.one()
            self.assertEqual(student.nombre, self.payload["nombres"])
            self.assertEqual(student.apellido, self.payload["apellidos"])
            self.assertEqual(student.nombre_completo, "María José Pérez-García")
            self.assertEqual(student.cup, self.payload["numero_unico"])
            self.assertEqual(student.cedula, self.payload["cedula"])
            self.assertEqual(student.sexo, self.payload["sexo"])
            self.assertEqual(user.email, self.payload["email"])
            self.assertEqual(user.rol, "Estudiante")
            self.assertEqual(user.id_estudiante, student.id_estudiante)
            self.assertNotEqual(user.password_hash, self.payload["password"])
            self.assertTrue(user.check_password(self.payload["password"]))
            self.assertIsNone(student.fecha_nacimiento)
            self.assertIsNone(student.id_pais_origen)
            self.assertTrue(user.activo)
        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)

    def test_login_by_code_email_and_identity_and_logout(self):
        self.assertEqual(self.register().status_code, 201)
        for identifier in (self.payload["numero_unico"].lower(), self.payload["email"].upper(), self.payload["cedula"]):
            response = self.client.post("/api/auth/login", json={"identifier": identifier, "password": self.payload["password"]})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["user"]["role"], "Estudiante")
            self.assertEqual(self.client.get("/api/auth/me").json["user"]["nombre"], "María José Pérez-García")
            self.assertEqual(self.client.post("/api/auth/logout").status_code, 200)
            self.assertEqual(self.client.get("/api/auth/me").status_code, 401)

    def test_rejects_csrf_and_non_json(self):
        self.assertEqual(self.client.post("/api/auth/register", json=self.payload).status_code, 403)
        self.assertEqual(self.client.post("/api/auth/register", data=self.payload).status_code, 415)
        self.assert_empty()

    def test_rejects_invalid_fields_and_privilege_injection(self):
        cases = [{}, [], {**self.payload, "rol": "Rector"}, {**self.payload, "persona_id": "existing"}]
        for field, value in (("email", "x@outlook.com.evil.test"), ("email", "x@gmail.com"),
                             ("password", "12345678"), ("password", "short!"), ("password", {}),
                             ("sexo", "Administrador"), ("numero_unico", "bad code"),
                             ("nombres", "<script>"), ("apellidos", "123"), ("cedula", "001-310299-1004A")):
            cases.append({**self.payload, field: value})
        for payload in cases:
            self.assertEqual(self.register(payload).status_code, 400)
            self.assert_empty()

    def test_duplicates_are_rejected_without_linking_existing_person(self):
        self.assertEqual(self.register().status_code, 201)
        for field in ("email", "numero_unico", "cedula"):
            other = {**self.payload, "email": "different@outlook.com", "numero_unico": "OTHER-1", "cedula": "001-120503-2004A"}
            other[field] = self.payload[field].swapcase()
            self.assertEqual(self.register(other).status_code, 409)
        with self.app.app_context():
            self.assertEqual([Estudiante.query.count(), Usuario.query.count()], [1, 1])
            db.session.add(Usuario(email=self.payload["email"].upper(), nombre_usuario="duplicate", password_hash="unused", rol="Consulta"))
            with self.assertRaises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_database_failure_does_not_leave_partial_records(self):
        with patch("core.registration.db.session.commit", side_effect=SQLAlchemyError("simulated")):
            self.assertEqual(self.register().status_code, 503)
        self.assert_empty()

    def test_students_cannot_access_staff_routes_or_choose_admin_view(self):
        self.register()
        self.client.post("/api/auth/login", json={"identifier": self.payload["email"], "password": self.payload["password"]})
        for method, path in (("get", "/api/asistencia/buscar-estudiantes"), ("get", "/api/stats/globales"),
                             ("post", "/api/v1/sync"), ("post", "/api/eventos"), ("get", "/api/v1/sync/nodes")):
            self.assertEqual(getattr(self.client, method)(path, json={}).status_code, 403, path)
        for path in ("/rector", "/usuarios.html", "/api/views/usuarios"):
            self.assertIn(self.client.get(path).status_code, (302, 403))
        page = self.client.get("/?role=admin").get_data(as_text=True)
        self.assertIn('data-account-role="Estudiante"', page)
        self.assertNotIn('data-set-role="admin"', page)
        self.assertIn("María José Pérez-García", page)

    def test_registration_rate_limit_cannot_be_bypassed_with_forwarded_header(self):
        from middleware.rate_limiter import rate_limiter
        rate_limiter._memory_storage.clear()
        self.app.config["RATE_LIMIT_ENABLED"] = True
        for _ in range(5):
            self.assertEqual(self.register({}).status_code, 400)
        csrf = self.client.get("/api/auth/registration-csrf").json["csrf_token"]
        response = self.client.post("/api/auth/register", json=self.payload,
                                    headers={"X-CSRF-Token": csrf, "X-Forwarded-For": "192.0.2.22"})
        self.assertEqual(response.status_code, 429)
        rate_limiter._memory_storage.clear()
