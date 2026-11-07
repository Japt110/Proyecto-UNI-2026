"""Regresiones de login/logout con una base SQLite aislada en memoria."""

import base64
import hashlib
import hmac
import json
import time
import unittest

from app import create_app
from database import db
from models.auth import AuthSession
from models.base import Usuario


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {}, "SQLALCHEMY_BINDS": {},
            "SECRET_KEY": "test-only-session-key", "RATE_LIMIT_ENABLED": False,
            "CACHE_TYPE": "SimpleCache", "SESSION_COOKIE_SECURE": False,
        })
        with self.app.app_context():
            user = Usuario(email="test@example.invalid", nombre_usuario="test_user", rol="Coordinador", activo=True)
            user.set_password("test-password")
            db.session.add(user)
            db.session.commit()
        self.client = self.app.test_client()

    def login(self, client=None):
        response = (client or self.client).post("/api/auth/login", json={
            "identifier": "test@example.invalid", "password": "test-password",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        return response.json["session_token"]

    def signed(self, payload):
        encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        sig = hmac.new(self.app.secret_key.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        return f"{encoded}.{sig}"

    def test_logout_revokes_token_cookie_and_refreshed_token(self):
        token = self.login()
        old_cookie = self.client.get_cookie("session").value
        refreshed = self.client.get("/api/auth/me").json["session_token"]
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.post("/api/auth/logout").status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)
        self.assertIsNone(self.client.get_cookie("session"))
        for credential in (token, refreshed):
            replay = self.app.test_client()
            self.assertEqual(replay.get("/api/auth/me", headers={"Authorization": f"Bearer {credential}"}).status_code, 401)
        replay = self.app.test_client()
        replay.set_cookie("session", old_cookie)
        self.assertEqual(replay.get("/api/auth/me").status_code, 401)
        with self.app.app_context():
            self.assertEqual(AuthSession.query.count(), 0)

    def test_logout_is_idempotent_and_login_works_again(self):
        self.login()
        for _ in range(2):
            self.assertTrue(self.client.post("/api/auth/logout").json["success"])
        self.assertEqual(self.client.get("/login").status_code, 200)
        self.login()
        self.assertEqual(self.client.get("/api/auth/me").status_code, 200)

    def test_token_only_logout_preserves_independent_session(self):
        token = self.login()
        other = self.app.test_client()
        self.login(other)
        token_client = self.app.test_client()
        response = token_client.post("/api/auth/logout", headers={"X-Session-Token": token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)
        self.assertEqual(other.get("/api/auth/me").status_code, 200)

    def test_expired_and_legacy_sessions_are_rejected(self):
        token = self.login()
        payload = json.loads(base64.b64decode(token.split(".")[0]))
        with self.app.app_context():
            active = AuthSession.query.one()
            active.expires_at = int(time.time()) - 1
            db.session.commit()
        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)
        payload.pop("sid")
        legacy = self.signed(payload)
        self.assertEqual(self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {legacy}"}).status_code, 401)

    def test_tampered_tokens_and_missing_expiration_are_rejected(self):
        token = self.login()
        payload = json.loads(base64.b64decode(token.split(".")[0]))
        payload.pop("exp")
        bad = [token + "x", "malformed", self.signed(payload)]
        for token in bad:
            with self.subTest(token=token[:8]):
                self.assertEqual(self.app.test_client().get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code, 401)

    def test_token_roles_do_not_override_database_permissions(self):
        token = self.login()
        payload = json.loads(base64.b64decode(token.split(".")[0]))
        payload["role"] = "Rector"
        response = self.app.test_client().get("/api/auth/me", headers={"Authorization": f"Bearer {self.signed(payload)}"})
        self.assertEqual(response.json["user"]["role"], "Coordinador")

    def test_catalog_aliases_require_session_and_html_is_not_cached(self):
        for path in ("/", "/index.html", "/pasantias", "/api/views/", "/api/views/pasantias"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.headers["Location"], "/login")
            self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.login()
        self.assertEqual(self.client.get("/index.html").headers["Cache-Control"], "no-store")


if __name__ == "__main__":
    unittest.main()
