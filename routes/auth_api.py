"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - API DE AUTENTICACIÓN Y SESIONES (`/api/auth`)
===============================================================================
Endpoints RESTful para:
- POST /api/auth/register    : Registro de nuevos usuarios (Estudiantes / Supervisores / Empresas).
- POST /api/auth/login       : Paso 1 - Validación de credenciales y envío de código 2FA por correo.
- POST /api/auth/verify-2fa  : Paso 2 - Verificación del código 2FA y establecimiento de sesión.
- POST /api/auth/resend-2fa  : Reenvío del código 2FA al correo registrado.
- POST /api/auth/logout      : Cierre de sesión formal y registro en AuditoriaSesiones.
- GET  /api/auth/me          : Perfil y credenciales del usuario autenticado en sesión actual.
===============================================================================
"""

import hmac
import hashlib
import json
import time
import uuid
import secrets
from datetime import datetime, timezone, timedelta, date
from flask import Blueprint, request, jsonify, session, current_app
from flask_mail import Message
from database import db
from extensions import mail
from models.usuarios_auditoria import Usuario, AuditoriaSesiones, AuditoriaCambios
from models.perfil_estudiante import Estudiante, Matricula
from models.actores_externos import TutorDocente, SupervisorInstitucional, EntidadReceptora
from core.security import verify_password, login_required

auth_bp = Blueprint("auth_api", __name__)


def _mask_email(email: str) -> str:
    """Enmascara una dirección de correo para despliegue seguro (ej. c***a@uni.edu.ni)."""
    if not email or "@" not in email:
        return "usuario@dominio.ni"
    user_part, domain = email.split("@", 1)
    if len(user_part) <= 2:
        masked_user = user_part[0] + "***"
    else:
        masked_user = user_part[0] + "***" + user_part[-1]
    return f"{masked_user}@{domain}"


def _build_session_token(usuario: Usuario) -> str:
    """
    Genera un token de sesión firmado con HMAC-SHA256 que encapsula la identidad y rol del usuario.
    """
    now = int(time.time())
    payload = {
        "uid": usuario.id_usuario,
        "username": usuario.nombre_usuario,
        "role": usuario.rol,
        "email": usuario.email,
        "id_estudiante": usuario.id_estudiante,
        "id_tutor": usuario.id_tutor,
        "id_supervisor": usuario.id_supervisor,
        "iat": now,
        "exp": now + 30 * 86400 if session.permanent else now + 8 * 3600,
    }
    payload_b64 = __import__('base64').b64encode(
        json.dumps(payload, separators=(',', ':')).encode()
    ).decode()

    secret = current_app.config.get("SECRET_KEY", "pasantias-uni-secret-key-permanente-2026")
    sig = hmac.new(
        secret.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).hexdigest()

    return f"{payload_b64}.{sig}"


def _get_user_display_name(usuario: Usuario) -> tuple[str, str | None]:
    """Retorna el nombre completo y CUP según la personificación del usuario."""
    if usuario.estudiante:
        return f"{usuario.estudiante.nombre} {usuario.estudiante.apellido}", usuario.estudiante.cup
    if usuario.tutor:
        return f"{usuario.tutor.nombre} {usuario.tutor.apellido}", None
    if usuario.supervisor:
        return f"{usuario.supervisor.nombre} {usuario.supervisor.apellido}", None
    return usuario.nombre_usuario, None


def _enviar_correo_2fa(usuario: Usuario, otp_code: str) -> bool:
    """
    Envía el código de verificación 2FA mediante Flask-Mail utilizando la configuración modular del sistema (.env).
    Si el servidor SMTP no está configurado en local, captura la excepción y la registra.
    """
    system_name = current_app.config.get("SYSTEM_NAME", "Sistema Web de Control de Pasantías")
    institution_name = current_app.config.get("INSTITUTION_NAME", "Universidad Nacional de Ingeniería")
    institution_short = current_app.config.get("INSTITUTION_SHORT", "UNI")
    sender = current_app.config.get("MAIL_DEFAULT_SENDER")
    expiration_minutes = current_app.config.get("SECURITY_2FA_EXPIRATION_MINUTES", 10)
    contact_email = current_app.config.get("INSTITUTION_CONTACT_EMAIL", "vinculacion@uni.edu.ni")

    subject = f"Código de Verificación 2FA: {otp_code} - {institution_short}"
    body_text = (
        f"Hola {usuario.nombre_usuario},\n\n"
        f"Tu código de autenticación de dos factores (2FA) es: {otp_code}\n\n"
        f"Este código es de un solo uso y expirará en {expiration_minutes} minutos.\n"
        f"Si no has solicitado este código, por favor repórtalo de inmediato a {contact_email}.\n\n"
        f"{system_name} - {institution_name}"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Código de Seguridad 2FA</title>
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #F3F4F6; margin: 0; padding: 24px;">
      <div style="max-width: 520px; margin: 0 auto; background-color: #FFFFFF; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <div style="background-color: #033E8C; padding: 24px; text-align: center; color: #FFFFFF;">
          <h2 style="margin: 0; font-size: 20px; font-weight: 700;">{institution_name}</h2>
          <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.9;">{system_name}</p>
        </div>
        <div style="padding: 32px 28px;">
          <h3 style="color: #1F2937; margin: 0 0 12px 0; font-size: 18px;">Autenticación en 2 Pasos (2FA)</h3>
          <p style="color: #4B5563; font-size: 14px; line-height: 1.5; margin: 0 0 24px 0;">
            Hola <strong>{usuario.nombre_usuario}</strong>, hemos recibido una solicitud de inicio de sesión para tu cuenta. Introduce el siguiente código de seguridad para verificar tu identidad:
          </p>
          <div style="background-color: #EFF6FF; border: 2px dashed #3B82F6; border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 24px;">
            <div style="color: #1E40AF; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px;">Código de Verificación</div>
            <div style="font-size: 34px; font-weight: 800; letter-spacing: 8px; color: #033E8C;">{otp_code}</div>
            <div style="color: #6B7280; font-size: 12px; margin-top: 6px;">Válido durante {expiration_minutes} minutos</div>
          </div>
          <p style="color: #6B7280; font-size: 12px; line-height: 1.4; margin: 0;">
            Si tú no solicitaste este acceso, por favor ignora este correo o contacta a la Oficina de Vinculación Universitaria ({contact_email}).
          </p>
        </div>
        <div style="background-color: #F9FAFB; padding: 16px 24px; text-align: center; border-top: 1px solid #E5E7EB;">
          <p style="color: #9CA3AF; font-size: 11px; margin: 0;">© 2026 {institution_name} · Dirección de Informática</p>
        </div>
      </div>
    </body>
    </html>
    """

    try:
        msg = Message(
            subject=subject,
            sender=sender,
            recipients=[usuario.email],
            body=body_text,
            html=html_content,
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.warning(f"[2FA Flask-Mail] No se pudo conectar al servidor SMTP: {e}. Desplegando en bitácora local: OTP={otp_code}")
        return False


# -----------------------------------------------------------------------------
# 1. POST /api/auth/register - Registro de Nuevos Usuarios
# -----------------------------------------------------------------------------

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registra una nueva cuenta de usuario en la plataforma.
    Soporta los perfiles:
    - 'Estudiante': Crea el perfil en estudiantes y genera matrícula activa.
    - 'Supervisor': Crea la entidad receptora (en espera) y el supervisor.
    - 'Administrador' / 'Tutor': Roles institucionales.
    """
    data = request.get_json() or {}
    nombre_usuario = (data.get("nombre_usuario") or data.get("username") or "").strip().lower()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    rol = (data.get("rol") or data.get("role") or "Estudiante").strip()
    nombre = (data.get("nombre") or "").strip()
    apellido = (data.get("apellido") or "").strip()

    if not nombre_usuario or not email or not password:
        return jsonify({"success": False, "message": "Nombre de usuario, correo electrónico y contraseña son obligatorios"}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "La contraseña debe tener al menos 6 caracteres"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"success": False, "message": "El formato del correo electrónico no es válido"}), 400

    # Comprobar unicidad de usuario y correo
    if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
        return jsonify({"success": False, "message": f"El nombre de usuario '{nombre_usuario}' ya se encuentra registrado"}), 409

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": f"El correo electrónico '{email}' ya se encuentra registrado"}), 409

    id_estudiante = None
    id_supervisor = None
    id_tutor = None

    # Creación de perfiles vinculados
    if rol.lower() == "estudiante":
        cup = (data.get("cup") or "").strip().upper()
        cedula = (data.get("cedula") or "").strip().upper()

        if not cup:
            cup = f"CUP-2026-{secrets.randbelow(900) + 100}"
        if not cedula:
            cedula = f"001-{secrets.randbelow(900000) + 100000}-{secrets.randbelow(9000) + 1000}A"

        # Verificar unicidad de cup y cedula
        if Estudiante.query.filter_by(cup=cup).first():
            cup = f"CUP-2026-{secrets.randbelow(9000) + 1000}"
        if Estudiante.query.filter_by(cedula=cedula).first():
            cedula = f"001-{secrets.randbelow(900000) + 100000}-0002A"

        estudiante = Estudiante(
            cup=cup,
            cedula=cedula,
            nombre=nombre or nombre_usuario.capitalize(),
            apellido=apellido or "Estudiante",
            fecha_nacimiento=date(2003, 1, 1),
            edad=23,
            sexo=data.get("sexo", "Masculino"),
            dimension_nacional="Urbana",
            id_pais_origen=1,
            id_etnia=1,
            estado_civil="Soltero",
            hijos=0,
        )
        db.session.add(estudiante)
        db.session.flush()

        # Generar matrícula activa en 4to año para elegibilidad de pasantías (CU-01 / CU-09)
        anio_academico = int(data.get("anio_academico", 4))
        matricula = Matricula(
            id_estudiante=estudiante.id_estudiante,
            id_carrera=int(data.get("id_carrera", 1)),
            periodo_academico="I Semestre 2026",
            anio_academico=anio_academico,
            modalidad="Regular",
            turno="Matutino",
            grupo_clase=f"{anio_academico}M1",
            estado="Activa",
        )
        db.session.add(matricula)
        id_estudiante = estudiante.id_estudiante
        rol = "Estudiante"

    elif rol.lower() in ("supervisor", "empresa"):
        empresa_nombre = (data.get("empresa_nombre") or data.get("empresa") or f"Empresa de {nombre_usuario}").strip()
        
        # Buscar o crear la entidad receptora
        entidad = EntidadReceptora.query.filter_by(nombre=empresa_nombre).first()
        if not entidad:
            entidad = EntidadReceptora(
                nombre=empresa_nombre,
                tipo=data.get("tipo_empresa", "Privada"),
                contacto_nombre=f"{nombre} {apellido}".strip(),
                contacto_email=email,
                contacto_telefono=data.get("telefono"),
                estado_aprobacion="Pendiente_Aprobacion",  # CU-05
            )
            db.session.add(entidad)
            db.session.flush()

        supervisor = SupervisorInstitucional(
            nombre=nombre or nombre_usuario.capitalize(),
            apellido=apellido or "Supervisor",
            cargo=data.get("cargo", "Encargado de Selección"),
            id_entidad=entidad.id_entidad,
        )
        db.session.add(supervisor)
        db.session.flush()
        id_supervisor = supervisor.id_supervisor
        rol = "Supervisor"

    nuevo_usuario = Usuario(
        nombre_usuario=nombre_usuario,
        email=email,
        rol=rol,
        activo=True,
        id_estudiante=id_estudiante,
        id_supervisor=id_supervisor,
        id_tutor=id_tutor,
    )
    nuevo_usuario.set_password(password)

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Usuario registrado exitosamente. Ahora puede iniciar sesión.",
        "user": {
            "id": nuevo_usuario.id_usuario,
            "username": nuevo_usuario.nombre_usuario,
            "email": nuevo_usuario.email,
            "role": nuevo_usuario.rol,
        }
    }), 201


# -----------------------------------------------------------------------------
# 2. POST /api/auth/login - Paso 1: Credenciales y Despacho de Código 2FA
# -----------------------------------------------------------------------------

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Paso 1 del Login:
    - Valida credenciales polimórficas (nombre de usuario, email, CUP o cédula).
    - Genera código OTP de 6 dígitos seguro.
    - Envía el código 2FA al correo registrado con Flask-Mail.
    - Deja la sesión en estado '2fa_pending' hasta la confirmación del código.
    """
    data = request.get_json() or {}
    identifier = (data.get("identifier") or data.get("username") or "").strip()
    password = data.get("password") or ""
    remember_me = bool(data.get("remember_me", False))

    ip_origen = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "")[:255]

    if not identifier or not password:
        return jsonify({"success": False, "message": "Credenciales incompletas"}), 400

    # 1. Búsqueda directa por nombre_usuario o email
    usuario = Usuario.query.filter(
        (Usuario.nombre_usuario == identifier) | (Usuario.email == identifier)
    ).first()

    # 2. Resolución polimórfica por CUP o Cédula de Estudiante
    if not usuario:
        est = Estudiante.query.filter(
            (Estudiante.cup == identifier) | (Estudiante.cedula == identifier)
        ).first()
        if est and est.usuario:
            usuario = est.usuario

    # 3. Validación de contraseña
    if not usuario or not usuario.check_password(password):
        aud_fallo = AuditoriaSesiones(
            id_usuario=usuario.id_usuario if usuario else None,
            nombre_usuario_intento=identifier,
            accion="FAILED_LOGIN",
            resultado="FALLIDO",
            ip_origen=ip_origen,
            user_agent=user_agent,
            detalle="Contraseña incorrecta o usuario no encontrado",
            sesion_id=str(uuid.uuid4()),
        )
        db.session.add(aud_fallo)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

        return jsonify({"success": False, "message": "Usuario o contraseña incorrectos"}), 401

    if not usuario.activo:
        return jsonify({"success": False, "message": "Esta cuenta se encuentra inactiva. Contacte al administrador."}), 403

    # =========================================================================
    # VERIFICACIÓN DE POLÍTICA 2FA DEL USUARIO (has_2fa)
    # =========================================================================
    if not getattr(usuario, "has_2fa", False):
        # El usuario tiene 2FA desactivado por defecto: Acceso directo a la plataforma
        sesion_id = str(uuid.uuid4())
        session.clear()
        session["user_id"] = usuario.id_usuario
        session["user_role"] = usuario.rol
        session["sesion_id"] = sesion_id

        if remember_me:
            session.permanent = True
            remember_days = current_app.config.get("SECURITY_REMEMBER_DAYS", 30)
            current_app.permanent_session_lifetime = timedelta(days=remember_days)
        else:
            session.permanent = False
            session_hours = current_app.config.get("SECURITY_SESSION_LIFETIME_HOURS", 8)
            current_app.permanent_session_lifetime = timedelta(hours=session_hours)

        aud_exito = AuditoriaSesiones(
            id_usuario=usuario.id_usuario,
            nombre_usuario_intento=usuario.nombre_usuario,
            accion="LOGIN_DIRECTO",
            resultado="EXITOSO",
            ip_origen=ip_origen,
            user_agent=user_agent,
            detalle=f"Inicio de sesión exitoso sin 2FA (rol: {usuario.rol}). Recordar sesión: {remember_me}",
            sesion_id=sesion_id,
        )
        db.session.add(aud_exito)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

        nombre_completo, cup = _get_user_display_name(usuario)
        token = _build_session_token(usuario)

        return jsonify({
            "success": True,
            "requires_2fa": False,
            "message": f"Inicio de sesión exitoso. Bienvenido {usuario.nombre_usuario}",
            "remember_me": remember_me,
            "session_token": token,
            "token": token,
            "redirect_url": "/",
            "user": {
                "id": usuario.id_usuario,
                "username": usuario.nombre_usuario,
                "email": usuario.email,
                "role": usuario.rol,
                "has_2fa": False,
                "nombre_completo": nombre_completo,
                "cup": cup,
                "id_estudiante": usuario.id_estudiante,
                "id_tutor": usuario.id_tutor,
                "id_supervisor": usuario.id_supervisor,
            }
        }), 200

    # =========================================================================
    # AUTENTICACIÓN DE 2 PASOS (2FA ACTIVO): GENERACIÓN Y ENVÍO DE CÓDIGO OTP
    # =========================================================================
    otp_code = f"{secrets.randbelow(900000) + 100000}"  # 6 dígitos numéricos
    exp_minutes = current_app.config.get("SECURITY_2FA_EXPIRATION_MINUTES", 10)
    expiracion_epoch = int(time.time()) + (exp_minutes * 60)

    session.clear()
    session["2fa_pending"] = True
    session["2fa_user_id"] = usuario.id_usuario
    session["2fa_code"] = otp_code
    session["2fa_expires"] = expiracion_epoch
    session["2fa_remember_me"] = remember_me

    # Envío del código por correo electrónico vía Flask-Mail
    mail_sent = _enviar_correo_2fa(usuario, otp_code)
    masked_email = _mask_email(usuario.email)

    resp_payload = {
        "success": True,
        "requires_2fa": True,
        "message": f"Código de verificación de 2 pasos enviado a {masked_email}",
        "email_masked": masked_email,
        "expires_in_seconds": exp_minutes * 60,
        "user_hint": usuario.nombre_usuario,
    }

    # Si estamos en modo de desarrollo / testing o el servidor SMTP no despachó, se incluye para pruebas automáticas
    if current_app.config.get("DEBUG") or current_app.config.get("ENV") == "development" or not mail_sent:
        resp_payload["dev_otp_preview"] = otp_code

    return jsonify(resp_payload), 200


# -----------------------------------------------------------------------------
# 3. POST /api/auth/verify-2fa - Paso 2: Verificación de Código y Creación de Sesión
# -----------------------------------------------------------------------------

@auth_bp.route("/verify-2fa", methods=["POST"])
def verify_2fa():
    """
    Paso 2 del Login:
    - Valida el código OTP de 6 dígitos.
    - Valida vigencia de tiempo (10 minutos).
    - Aplica la política de 'Recordar Sesión' (session.permanent = True por 30 días).
    - Finaliza la autenticación formal del usuario.
    """
    data = request.get_json() or {}
    code = str(data.get("code") or data.get("otp") or "").strip()
    remember_me_req = data.get("remember_me")

    if not session.get("2fa_pending") or not session.get("2fa_user_id"):
        return jsonify({
            "success": False,
            "message": "No hay un proceso de autenticación 2FA pendiente o la sesión ha expirado. Inicie sesión nuevamente."
        }), 400

    # Validar expiración
    ahora = int(time.time())
    if ahora > session.get("2fa_expires", 0):
        session.clear()
        return jsonify({
            "success": False,
            "message": "El código de verificación ha expirado (límite: 10 minutos). Solicite uno nuevo."
        }), 401

    # Validar código
    codigo_esperado = str(session.get("2fa_code", ""))
    if not code or code != codigo_esperado:
        return jsonify({
            "success": False,
            "message": "Código de verificación incorrecto. Por favor revise el código enviado a su correo."
        }), 401

    # Código válido: formalizar sesión
    user_id = session.get("2fa_user_id")
    remember_me = session.get("2fa_remember_me", False) if remember_me_req is None else bool(remember_me_req)

    usuario = Usuario.query.get(user_id)
    if not usuario:
        session.clear()
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    # Limpiar estado temporal 2FA y establecer identidad
    sesion_id = str(uuid.uuid4())
    session.clear()
    session["user_id"] = usuario.id_usuario
    session["user_role"] = usuario.rol
    session["sesion_id"] = sesion_id

    # =========================================================================
    # POLÍTICA DE RECORDAR SESIÓN (REMEMBER ME)
    # =========================================================================
    if remember_me:
        session.permanent = True
        remember_days = current_app.config.get("SECURITY_REMEMBER_DAYS", 30)
        current_app.permanent_session_lifetime = timedelta(days=remember_days)
    else:
        session.permanent = False
        session_hours = current_app.config.get("SECURITY_SESSION_LIFETIME_HOURS", 8)
        current_app.permanent_session_lifetime = timedelta(hours=session_hours)

    # Registrar auditoría de inicio exitoso
    ip_origen = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "")[:255]
    aud_exito = AuditoriaSesiones(
        id_usuario=usuario.id_usuario,
        nombre_usuario_intento=usuario.nombre_usuario,
        accion="LOGIN_2FA",
        resultado="EXITOSO",
        ip_origen=ip_origen,
        user_agent=user_agent,
        detalle=f"Autenticación 2FA exitosa con rol {usuario.rol}. Recordar sesión: {remember_me}",
        sesion_id=sesion_id,
    )
    db.session.add(aud_exito)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    nombre_completo, cup = _get_user_display_name(usuario)
    token = _build_session_token(usuario)

    return jsonify({
        "success": True,
        "message": "Autenticación de 2 pasos completada exitosamente",
        "remember_me": remember_me,
        "session_token": token,
        "user": {
            "id": usuario.id_usuario,
            "username": usuario.nombre_usuario,
            "email": usuario.email,
            "role": usuario.rol,
            "nombre_completo": nombre_completo,
            "cup": cup,
            "id_estudiante": usuario.id_estudiante,
            "id_tutor": usuario.id_tutor,
            "id_supervisor": usuario.id_supervisor,
        }
    }), 200


# -----------------------------------------------------------------------------
# 4. POST /api/auth/resend-2fa - Reenvío de Código 2FA
# -----------------------------------------------------------------------------

@auth_bp.route("/resend-2fa", methods=["POST"])
def resend_2fa():
    """Genera un nuevo código OTP y lo envía nuevamente al correo del usuario."""
    if not session.get("2fa_pending") or not session.get("2fa_user_id"):
        return jsonify({
            "success": False,
            "message": "No hay un proceso 2FA pendiente para reenviar código."
        }), 400

    usuario = Usuario.query.get(session.get("2fa_user_id"))
    if not usuario:
        session.clear()
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    nuevo_otp = f"{secrets.randbelow(900000) + 100000}"
    exp_minutes = current_app.config.get("SECURITY_2FA_EXPIRATION_MINUTES", 10)
    session["2fa_code"] = nuevo_otp
    session["2fa_expires"] = int(time.time()) + (exp_minutes * 60)

    mail_sent = _enviar_correo_2fa(usuario, nuevo_otp)
    masked_email = _mask_email(usuario.email)

    resp_payload = {
        "success": True,
        "message": f"Nuevo código enviado exitosamente a {masked_email}",
        "email_masked": masked_email,
        "expires_in_seconds": exp_minutes * 60,
    }

    if current_app.config.get("DEBUG") or current_app.config.get("ENV") == "development" or not mail_sent:
        resp_payload["dev_otp_preview"] = nuevo_otp

    return jsonify(resp_payload), 200


# -----------------------------------------------------------------------------
# 5. POST /api/auth/logout - Cierre de Sesión
# -----------------------------------------------------------------------------

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Destruye la sesión activa y registra el evento en auditoria_sesiones."""
    user_id = session.get("user_id")
    sesion_id = session.get("sesion_id")

    if user_id:
        aud_logout = AuditoriaSesiones(
            id_usuario=user_id,
            nombre_usuario_intento=None,
            accion="LOGOUT",
            resultado="EXITOSO",
            ip_origen=request.headers.get("X-Forwarded-For", request.remote_addr),
            user_agent=request.headers.get("User-Agent", "")[:255],
            detalle="Cierre de sesión regular del usuario",
            sesion_id=sesion_id or str(uuid.uuid4()),
        )
        db.session.add(aud_logout)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    session.clear()
    return jsonify({"success": True, "message": "Sesión cerrada correctamente"}), 200


# -----------------------------------------------------------------------------
# 6. GET /api/auth/me - Obtención del Usuario en Sesión Activa
# -----------------------------------------------------------------------------

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """Retorna los datos del usuario autenticado en sesión y renueva el token."""
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id)
    if not usuario:
        session.clear()
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    nombre_completo, cup = _get_user_display_name(usuario)

    return jsonify({
        "success": True,
        "user": {
            "id": usuario.id_usuario,
            "username": usuario.nombre_usuario,
            "email": usuario.email,
            "role": usuario.rol,
            "nombre_completo": nombre_completo,
            "cup": cup,
            "id_estudiante": usuario.id_estudiante,
            "id_tutor": usuario.id_tutor,
            "id_supervisor": usuario.id_supervisor,
            "has_2fa": bool(getattr(usuario, "has_2fa", False)),
        },
        "session_token": _build_session_token(usuario),
    }), 200


# -----------------------------------------------------------------------------
# 7. PUT /api/auth/toggle-2fa - Activación / Desactivación de 2FA
# -----------------------------------------------------------------------------

@auth_bp.route("/toggle-2fa", methods=["POST", "PUT"])
@login_required
def toggle_2fa():
    """Activa o desactiva la verificación en 2 pasos (2FA) para el usuario autenticado."""
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id) if user_id else None
    if not usuario:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    data = request.get_json(silent=True) or {}
    if "has_2fa" in data:
        usuario.has_2fa = bool(data["has_2fa"])
    else:
        usuario.has_2fa = not bool(usuario.has_2fa)

    db.session.commit()
    estado_txt = "activada" if usuario.has_2fa else "desactivada"
    return jsonify({
        "success": True,
        "message": f"Verificación en dos pasos (2FA) {estado_txt} exitosamente.",
        "has_2fa": bool(usuario.has_2fa)
    }), 200
