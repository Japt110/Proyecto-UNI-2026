"""
===============================================================================
EVENTOS-UNI - MÓDULO DE SEGURIDAD Y MIDDLEWARE (RBAC)
===============================================================================
Proporciona utilidades para hashing de contraseñas (PBKDF2-SHA256 con sal dinámica)
y decoradores de autorización para control de acceso basado en roles (RBAC).
===============================================================================
"""

import hmac
import hashlib
import json
import base64
import time
from functools import wraps
from typing import Callable, Any
from flask import session, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash


# -----------------------------------------------------------------------------
# 1. Hashing y Verificación de Contraseñas (OWASP Recommended Standards)
# -----------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    Genera un hash criptográficamente seguro utilizando PBKDF2:SHA256 con salt dinámico de 16 bytes.
    
    :param password: Contraseña en texto plano.
    :return: Cadena de hash seguro formateada.
    """
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


def verify_password(password_hash: str, password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash almacenado.
    
    :param password_hash: Hash PBKDF2 previamente generado.
    :param password: Contraseña a verificar.
    :return: True si coincide, False en caso contrario.
    """
    return check_password_hash(password_hash, password)


def verify_token_and_restore_session() -> bool:
    """
    Verifica el token de sesión enviado en las cabeceras HTTP (Authorization / X-Session-Token).
    Si el token es válido (firma HMAC limpia y fecha exp vigente), restaura la sesión de Flask.
    """
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
    elif request.headers.get("X-Session-Token"):
        token = request.headers.get("X-Session-Token").strip()

    if token and "." in token:
        try:
            parts = token.split(".")
            if len(parts) == 2:
                payload_b64, sig = parts[0], parts[1]
                secret = current_app.config.get("SECRET_KEY", "eventos-uni-secret-key-permanente-2026-production-v1")
                expected_sig = hmac.new(
                    secret.encode(),
                    payload_b64.encode(),
                    hashlib.sha256
                ).hexdigest()

                if hmac.compare_digest(sig, expected_sig):
                    padded_b64 = payload_b64 + "=" * (-len(payload_b64) % 4)
                    payload = json.loads(base64.b64decode(padded_b64).decode())
                    now = int(time.time())
                    if not payload.get("exp") or now <= payload["exp"]:
                        session["user_id"] = payload.get("uid")
                        session["user_role"] = payload.get("role")
                        return True
        except Exception:
            pass

    if "user_id" in session:
        return True

    return False


# -----------------------------------------------------------------------------
# 2. Middleware de Autenticación y Autorización por Roles (RBAC)
# -----------------------------------------------------------------------------

def login_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorador middleware que restringe el acceso a un endpoint exigiendo
    un estado de sesión autenticado activo o un token Bearer válido.
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not verify_token_and_restore_session():
            return jsonify({"success": False, "message": "Acceso denegado. Sesión no iniciada o token vencido."}), 401
        return f(*args, **kwargs)
    return decorated_function


def roles_required(*allowed_roles: str) -> Callable[..., Any]:
    """
    Decorador middleware para Control de Acceso Basado en Roles (RBAC).
    Restringe la ejecución de un endpoint a usuarios cuyo rol coincida con los roles autorizados.
    
    :param allowed_roles: Roles permitidos (ej. "Rector", "Encargado").
    """
    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            if not verify_token_and_restore_session():
                return jsonify({"success": False, "message": "Acceso denegado. No autenticado."}), 401

            user_role = session.get("user_role")
            if user_role not in allowed_roles:
                return jsonify({"success": False, "message": "Acceso denegado. Permisos insuficientes."}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator