"""
===============================================================================
EVENTOS-UNI - API REST DE AUTENTICACIÓN Y GESTIÓN DE SESIÓN (`/api/auth`)
===============================================================================
Proporciona los endpoints RESTful para:
- POST /api/auth/register: Alta transaccional de estudiante con validación y CSRF.
- GET /api/auth/registration-csrf: Protección del formulario de registro.
- POST /api/auth/login : Autenticación polimórfica (email, carné, cédula o código).
- POST /api/auth/logout: Cierre explícito de la sesión del usuario.
- GET  /api/auth/me    : Obtención del usuario autenticado en la sesión actual.
===============================================================================
"""

import hmac
import secrets
from flask import Blueprint, request, jsonify, session, current_app
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from database import db
from models.base import Usuario, Estudiante
from core.security import verify_password, login_required, verify_token_and_restore_session
from core.auth_sessions import build_session_token, start_session, revoke_current_session
from core.session_audit import record_access
from core.registration import register_student, RegistrationInvalid, RegistrationConflict

auth_bp = Blueprint("auth_api", __name__)


@auth_bp.after_request
def prevent_auth_caching(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@auth_bp.route("/registration-csrf", methods=["GET"])
def registration_csrf():
    token = session.get("registration_csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        session["registration_csrf"] = token
    return jsonify({"csrf_token": token})


@auth_bp.route("/register", methods=["POST"])
def register():
    if current_app.config.get("RATE_LIMIT_ENABLED", True):
        from middleware.rate_limiter import rate_limiter
        allowed, _ = rate_limiter.is_allowed(f"register:{request.remote_addr}", max_requests=5, window_seconds=300)
        if not allowed:
            return jsonify(success=False, message="Demasiados intentos. Inténtalo de nuevo en cinco minutos."), 429, {"Retry-After": "300"}
    if not request.is_json:
        return jsonify(success=False, message="Se requiere contenido JSON."), 415
    expected = session.get("registration_csrf", "")
    provided = request.headers.get("X-CSRF-Token", "")
    if not expected or not provided or not hmac.compare_digest(expected.encode(), provided.encode()):
        return jsonify(success=False, message="La sesión del formulario venció. Vuelve a intentarlo."), 403
    try:
        register_student(request.get_json(silent=True))
    except RegistrationInvalid as error:
        return jsonify(success=False, message="Revisa los campos indicados.", errors=error.errors), 400
    except RegistrationConflict:
        db.session.rollback()
        return jsonify(success=False, message="No se pudo crear la cuenta: el correo, código o cédula ya está registrado. Si los datos son tuyos, contacta al administrador."), 409
    except SQLAlchemyError as error:
        db.session.rollback()
        # No registrar parámetros SQL, contraseñas ni datos personales.
        current_app.logger.error("Registration storage failure: %s", type(error).__name__)
        return jsonify(success=False, message="No se pudo guardar la cuenta. Inténtalo más tarde."), 503
    session.pop("registration_csrf", None)
    return jsonify(success=True, message="Cuenta creada. Ya puedes iniciar sesión con tu código o correo."), 201


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
    data = request.get_json(silent=True)
    if (not isinstance(data, dict) or not isinstance(data.get("identifier"), str)
            or not isinstance(data.get("password"), str) or not data["identifier"].strip() or not data["password"]):
        return jsonify({"success": False, "message": "Credenciales incompletas"}), 400

    identifier = data.get("identifier").strip()
    password = data.get("password")

    usuario = Usuario.query.filter(func.lower(Usuario.email) == identifier.lower()).first()
    if not usuario:
        usuario = Usuario.query.join(Estudiante, Usuario.id_estudiante == Estudiante.id_estudiante).filter(
            (func.upper(Estudiante.cup) == identifier.upper()) | (func.upper(Estudiante.cedula) == identifier.upper())
        ).first()
    if not usuario:
        usuario = Usuario.query.filter(func.lower(Usuario.nombre_usuario) == identifier.lower()).first()

    # 3. Verificación criptográfica de la contraseña
    if not usuario or not usuario.activo or not verify_password(usuario.password_hash, password):
        record_access("LOGIN_FALLIDO", False, identifier=identifier)
        db.session.commit()
        return jsonify({"success": False, "message": "Usuario o contraseña incorrectos"}), 401

    # 4. Establecer sesión de servidor
    start_session(usuario)
    record_access("LOGIN_OK", True, usuario)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Autenticación exitosa",
        "session_token": build_session_token(usuario),
        "user": {
            "id": usuario.id,
            "email": usuario.email,
            "role": usuario.rol,
            "nombre": usuario.nombre_visible
        }
    }), 200


# -----------------------------------------------------------------------------
# 2. POST /api/auth/logout - Cierre de Sesión
# -----------------------------------------------------------------------------

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Cierre idempotente: una sesión ya vencida también puede cerrarse."""
    if verify_token_and_restore_session():
        usuario = db.session.get(Usuario, session.get("user_id"))
        record_access("LOGOUT", True, usuario)
    revoke_current_session()
    return jsonify({"success": True, "message": "Sesión cerrada correctamente"}), 200


# -----------------------------------------------------------------------------
# 3. GET /api/auth/me - Obtención del Usuario de la Sesión
# -----------------------------------------------------------------------------

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """Retorna el perfil del usuario autenticado almacenado en la sesión.
    Incluye un session_token renovado para que el cliente actualice su caché local."""
    usuario = db.session.get(Usuario, session.get("user_id"))
    if not usuario:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    return jsonify({
        "success": True,
        "session_token": build_session_token(usuario),
        "user": {
            "id": usuario.id,
            "email": usuario.email,
            "role": usuario.rol,
            "nombre_usuario": usuario.nombre_usuario,
            "ruta_imagen": usuario.ruta_imagen,
            "nombre": usuario.nombre_visible,
            "numero_unico": usuario.estudiante.cup if usuario.estudiante else None
        }
    }), 200
