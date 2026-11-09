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
    Verifica el token de sesión enviado en las cabeceras HTTP (Authorization / X-Session-Token)
    o la existencia de una sesión de servidor Flask activa.
    Si 2FA se encuentra pendiente, no se concede acceso autenticado.
    """
    # Si la sesión actual está en proceso intermedio de 2FA, no está autenticada completamente
    if session.get("2fa_pending"):
        return False

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

    if "user_id" in session and session.get("user_id") is not None:
        return True

    return False


def normalize_role(role: str | None) -> str:
    """Normaliza las variantes de nombres de rol a las claves canónicas del sistema."""
    if not role:
        return ""
    r = str(role).strip().lower()
    if r in ("administrador", "admin", "rector"):
        return "Administrador"
    if r in ("estudiante", "alumno"):
        return "Estudiante"
    if r in ("supervisor", "empresa", "empresario", "encargado"):
        return "Supervisor"
    if r in ("tutor", "docente"):
        return "Tutor"
    return str(role).strip()


# -----------------------------------------------------------------------------
# 2. Middleware de Autenticación y Autorización por Roles (RBAC)
# -----------------------------------------------------------------------------

def login_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorador middleware que restringe el acceso a un endpoint exigiendo
    un estado de sesión autenticado activo o un token Bearer válido.
    Para vistas HTML (como /index, /rector, etc.) redirige a /login.
    Para APIs RESTful, retorna respuesta JSON HTTP 401.
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not verify_token_and_restore_session():
            # Si es solicitud a API REST o petición AJAX/JSON
            if (
                request.path.startswith("/api/")
                or request.is_json
                or request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or "application/json" in request.headers.get("Accept", "")
            ):
                return jsonify({
                    "success": False,
                    "message": "Acceso denegado. Sesión no iniciada o token vencido."
                }), 401

            # Si es vista web en navegador, redirigir al login
            from flask import redirect
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def roles_required(*allowed_roles: str) -> Callable[..., Any]:
    """
    Decorador middleware para Control de Acceso Basado en Roles (RBAC).
    Garantiza que usuarios sin el rol requerido no puedan acceder al recurso.
    Si un estudiante intenta acceder a endpoints exclusivos de administradores,
    o si un administrador intenta acceder a endpoints exclusivos de estudiantes,
    se bloquea con HTTP 403 Forbidden.
    """
    normalized_allowed = {normalize_role(r) for r in allowed_roles}

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # 1. Verificar autenticación previa
            if not verify_token_and_restore_session():
                if (
                    request.path.startswith("/api/")
                    or request.is_json
                    or request.headers.get("X-Requested-With") == "XMLHttpRequest"
                    or "application/json" in request.headers.get("Accept", "")
                ):
                    return jsonify({"success": False, "message": "Acceso denegado. Sesión no iniciada o token vencido."}), 401
                from flask import redirect
                return redirect("/login")

            # 2. Verificar autorización de rol
            raw_role = session.get("user_role")
            current_role = normalize_role(raw_role)

            if current_role not in normalized_allowed:
                msg = f"Acceso denegado: El rol '{raw_role}' no tiene autorización para este recurso. Acción restringida exclusivamente a: {', '.join(allowed_roles)}."
                if (
                    request.path.startswith("/api/")
                    or request.is_json
                    or request.headers.get("X-Requested-With") == "XMLHttpRequest"
                    or "application/json" in request.headers.get("Accept", "")
                ):
                    return jsonify({
                        "success": False,
                        "message": msg,
                        "rol_actual": raw_role,
                        "roles_permitidos": list(allowed_roles)
                    }), 403

                # En vistas HTML devolver 403 con mensaje claro
                return f"""
                <div style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: #DC2626;">403 - Acceso Denegado</h2>
                    <p style="color: #4B5563;">{msg}</p>
                    <p><a href="/" style="color: #033E8C; text-decoration: underline;">Volver al Inicio</a></p>
                </div>
                """, 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorador exclusivo para Administradores de la Universidad."""
    return roles_required("Administrador")(f)


def student_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorador exclusivo para Estudiantes Universitarios."""
    return roles_required("Estudiante")(f)


def company_or_admin_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorador para Entidades Receptoras (Supervisores) y Administradores."""
    return roles_required("Supervisor", "Administrador")(f)