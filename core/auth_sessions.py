"""Ciclo de vida de sesiones: creación, validación y revocación persistente."""

import base64
import hashlib
import hmac
import json
import secrets
import time

from flask import current_app, request, session, g
from database import db
from models.auth import AuthSession
from models.base import Usuario


def _session_key(session_id: str) -> str:
    return hashlib.sha256(session_id.encode()).hexdigest()


def revoke_current_session() -> None:
    """Revoca la sesión actual antes de eliminar la cookie del navegador."""
    session_id = session.get("session_id")
    if session_id:
        AuthSession.query.filter_by(id=_session_key(session_id)).delete()
        db.session.commit()
    session.clear()


def start_session(usuario: Usuario) -> None:
    revoke_current_session()
    session_id = secrets.token_urlsafe(32)
    expires_at = int(time.time() + current_app.permanent_session_lifetime.total_seconds())
    db.session.add(AuthSession(id=_session_key(session_id), user_id=usuario.id, expires_at=expires_at))
    db.session.commit()
    session.update(session_id=session_id, user_id=usuario.id, user_role=usuario.rol,
                   expires_at=expires_at)
    session.permanent = True


def build_session_token(usuario: Usuario) -> str:
    """Mantiene el formato del cliente; solo el servidor valida la firma."""
    payload = {
        "sid": session["session_id"], "uid": usuario.id, "role": usuario.rol,
        "email": usuario.email, "iat": int(time.time()), "exp": session["expires_at"],
    }
    encoded = base64.b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
    signature = hmac.new(current_app.secret_key.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def authenticate_session() -> bool:
    """Acepta únicamente credenciales asociadas a una sesión activa en la BD."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:].strip() if auth_header.startswith("Bearer ") else request.headers.get("X-Session-Token")
    session_id, user_id = session.get("session_id"), session.get("user_id")
    if token:
        try:
            encoded, signature = token.split(".")
            expected = hmac.new(current_app.secret_key.encode(), encoded.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                return False
            payload = json.loads(base64.b64decode(encoded, validate=True))
            if not isinstance(payload, dict) or type(payload.get("exp")) is not int or payload["exp"] <= time.time():
                return False
            session_id, user_id = payload.get("sid"), payload.get("uid")
        except (ValueError, TypeError, UnicodeError):
            return False

    if not isinstance(session_id, str) or type(user_id) is not int:
        session.clear()
        return False
    active = db.session.get(AuthSession, _session_key(session_id))
    if not active or active.user_id != user_id or active.expires_at <= time.time():
        session.clear()
        return False
    usuario = db.session.get(Usuario, user_id)
    if not usuario or not usuario.activo:
        session.clear()
        return False
    # Los permisos proceden de la BD, nunca de las afirmaciones del cliente.
    session.update(session_id=session_id, user_id=usuario.id, user_role=usuario.rol,
                   expires_at=active.expires_at)
    session.permanent = True
    g.current_user = usuario
    return True
