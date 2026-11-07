"""Sesiones revocables; se almacena el hash del identificador, no el token."""

from database import db


class AuthSession(db.Model):
    __tablename__ = "auth_sessions"

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = db.Column(db.BigInteger, nullable=False, index=True)
