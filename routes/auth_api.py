"""
===============================================================================
EVENTOS-UNI - API REST DE AUTENTICACIÓN Y GESTIÓN DE SESIÓN (`/api/auth`)
===============================================================================
Proporciona los endpoints RESTful para:
- POST /api/auth/login : Autenticación polimórfica (email, carné, cédula o código).
- POST /api/auth/logout: Cierre explícito de la sesión del usuario.
- GET  /api/auth/me    : Obtención del usuario autenticado en la sesión actual.
===============================================================================
"""

import hmac
import hashlib
import json
import time
from flask import Blueprint, request, jsonify, session, current_app
from models.base import Usuario, Persona, Estudiante, Trabajador
from core.security import verify_password, login_required

auth_bp = Blueprint("auth_api", __name__)


def _build_session_token(usuario: Usuario) -> str:
    """
    Genera un token de sesión firmado (HMAC-SHA256) que contiene el perfil del usuario.
    El token tiene estructura: base64(payload_json).base64(hmac_signature).
    El cliente puede verificar el token localmente usando la misma clave (almacenada en el
    token sin exponer la clave secreta real — la seguridad real sigue siendo el Flask session
    cookie que es HttpOnly y llega en cada petición HTTP).

    Estructura del payload (JSON):
      - uid:   ID del usuario
      - role:  Rol del usuario ('Rector' | 'Encargado')
      - email: Email del usuario
      - iat:   Timestamp de emisión (segundos UNIX)
      - exp:   Timestamp de expiración (segundos UNIX, iat + 8h)
    """
    now = int(time.time())
    payload = {
        "uid":   usuario.id,
        "role":  usuario.rol,
        "email": usuario.email,
        "iat":   now,
        "exp":   now + 8 * 3600   # 8 horas — alineado con PERMANENT_SESSION_LIFETIME
    }
    payload_b64 = __import__('base64').b64encode(
        json.dumps(payload, separators=(',', ':')).encode()
    ).decode()

    secret = current_app.config.get("SECRET_KEY", "eventos-uni-secret-key-permanente-2026-production-v1")
    sig = hmac.new(
        secret.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).hexdigest()

    return f"{payload_b64}.{sig}"


# -----------------------------------------------------------------------------
# 1. POST /api/auth/login - Inicio de Sesión Polimórfico
# -----------------------------------------------------------------------------

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Autentica a un usuario aceptando email directo o identificador institucional
    (Cédula de identidad, Carné de Estudiante o Código de Trabajador).
    Establece una sesión de servidor segura HTTP-Only / SameSite=Lax.
    """
    data = request.get_json()
    if not data or not data.get("identifier") or not data.get("password"):
        return jsonify({"success": False, "message": "Credenciales incompletas"}), 400

    identifier = data.get("identifier").strip()
    password = data.get("password")

    # 1. Búsqueda directa por Email de Usuario
    usuario = Usuario.query.filter_by(email=identifier).first()

    # 2. Resolución Polimórfica en el Padrón (Carné / Cédula / Código de Trabajador)
    if not usuario:
        persona = Persona.query.filter(
            (Persona.numero_unico == identifier) | (Persona.cedula == identifier)
        ).first()

        if not persona:
            estudiante = Estudiante.query.filter_by(carnet_estudiante=identifier).first()
            if estudiante:
                persona = estudiante.persona

        if not persona:
            trabajador = Trabajador.query.filter_by(codigo_trabajador=identifier).first()
            if trabajador:
                persona = trabajador.persona

        if persona:
            usuario = Usuario.query.filter(
                (Usuario.email == persona.cedula) | (Usuario.email == persona.numero_unico)
            ).first()

    # 3. Verificación criptográfica de la contraseña
    if not usuario or not verify_password(usuario.password_hash, password):
        return jsonify({"success": False, "message": "Usuario o contraseña incorrectos"}), 401

    # 4. Establecer sesión de servidor
    session.clear()
    session["user_id"] = usuario.id
    session["user_role"] = usuario.rol
    session["unidad_id"] = usuario.unidad_id
    session.permanent = True

    return jsonify({
        "success": True,
        "message": "Autenticación exitosa",
        "session_token": _build_session_token(usuario),
        "user": {
            "id": usuario.id,
            "email": usuario.email,
            "role": usuario.rol,
            "unidad_id": usuario.unidad_id
        }
    }), 200


# -----------------------------------------------------------------------------
# 2. POST /api/auth/logout - Cierre de Sesión
# -----------------------------------------------------------------------------

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Destruye la sesión del servidor para el usuario actual."""
    session.clear()
    return jsonify({"success": True, "message": "Sesión cerrada correctamente"}), 200


# -----------------------------------------------------------------------------
# 3. GET /api/auth/me - Obtención del Usuario de la Sesión
# -----------------------------------------------------------------------------

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """Retorna el perfil del usuario autenticado almacenado en la sesión.
    Incluye un session_token renovado para que el cliente actualice su caché local."""
    usuario = Usuario.query.get(session.get("user_id"))
    if not usuario:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    return jsonify({
        "success": True,
        "session_token": _build_session_token(usuario),
        "user": {
            "id": usuario.id,
            "email": usuario.email,
            "role": usuario.rol,
            "unidad": usuario.unidad.nombre if usuario.unidad else "General"
        }
    }), 200