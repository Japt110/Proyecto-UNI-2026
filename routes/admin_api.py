"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - RUTAS ADMINISTRATIVAS Y GESTIÓN DE USUARIOS
===============================================================================
Controlador RESTful exclusivo para administradores de la universidad (RBAC: Administrador):
- GET  /api/admin/usuarios               : Listado paginado y filtrado multicriterio de usuarios
- GET  /api/admin/usuarios/<id>          : Detalle completo de usuario y personificación
- PUT  /api/admin/usuarios/<id>/toggle-activo : Activar / desactivar acceso de un usuario
- GET  /api/admin/usuarios/estadisticas  : Resumen de usuarios por rol y estado
===============================================================================
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session
from sqlalchemy import or_, and_, func
from database import db
from core.security import admin_required
from models.usuarios_auditoria import Usuario, AuditoriaCambios
from models.perfil_estudiante import Estudiante
from models.actores_externos import TutorDocente, SupervisorInstitucional

admin_bp = Blueprint("admin_api", __name__)


@admin_bp.route("/usuarios", methods=["GET"])
@admin_required
def listar_usuarios():
    """
    Lista todos los usuarios del sistema con paginación y filtros multicriterio:
    - Búsqueda global (q / busqueda)
    - Filtro por nombres reales (nombre)
    - Filtro por nombre de usuario (nombre_usuario / username)
    - Filtro por rol (rol: Administrador, Estudiante, Supervisor, Tutor)
    - Filtro por estado (estado: activo, inactivo)
    - Ordenamiento (orden: fecha_desc, fecha_asc, nombre_asc, usuario_asc)
    """
    try:
        # 1. Parámetros de paginación
        page = request.args.get("pagina", request.args.get("page", 1, type=int), type=int)
        per_page = request.args.get("por_pagina", request.args.get("per_page", 10, type=int), type=int)
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10

        # 2. Query base con Joins externos para filtrado de personificaciones
        query = Usuario.query.outerjoin(
            Estudiante, Usuario.id_estudiante == Estudiante.id_estudiante
        ).outerjoin(
            TutorDocente, Usuario.id_tutor == TutorDocente.id_tutor
        ).outerjoin(
            SupervisorInstitucional, Usuario.id_supervisor == SupervisorInstitucional.id_supervisor
        )

        # 3. Filtros
        busqueda = request.args.get("busqueda", request.args.get("q", "")).strip()
        filtro_nombre = request.args.get("nombre", "").strip()
        filtro_usuario = request.args.get("nombre_usuario", request.args.get("username", "")).strip()
        filtro_rol = request.args.get("rol", "").strip()
        filtro_estado = request.args.get("estado", "").strip().lower()

        # Búsqueda global
        if busqueda:
            term = f"%{busqueda}%"
            query = query.filter(
                or_(
                    Usuario.nombre_usuario.ilike(term),
                    Usuario.email.ilike(term),
                    Estudiante.nombre.ilike(term),
                    Estudiante.apellido.ilike(term),
                    Estudiante.cup.ilike(term),
                    Estudiante.cedula.ilike(term),
                    TutorDocente.nombre.ilike(term),
                    TutorDocente.apellido.ilike(term),
                    SupervisorInstitucional.nombre.ilike(term),
                    SupervisorInstitucional.apellido.ilike(term),
                )
            )

        # Filtro específico de nombres personales
        if filtro_nombre:
            n_term = f"%{filtro_nombre}%"
            query = query.filter(
                or_(
                    Estudiante.nombre.ilike(n_term),
                    Estudiante.apellido.ilike(n_term),
                    TutorDocente.nombre.ilike(n_term),
                    TutorDocente.apellido.ilike(n_term),
                    SupervisorInstitucional.nombre.ilike(n_term),
                    SupervisorInstitucional.apellido.ilike(n_term),
                )
            )

        # Filtro específico de nombre de usuario
        if filtro_usuario:
            query = query.filter(Usuario.nombre_usuario.ilike(f"%{filtro_usuario}%"))

        # Filtro de rol
        if filtro_rol and filtro_rol.lower() not in ("todos", "all", ""):
            query = query.filter(Usuario.rol.ilike(filtro_rol))

        # Filtro de estado activo / inactivo
        if filtro_estado in ("activo", "activa", "true", "1"):
            query = query.filter(Usuario.activo.is_(True))
        elif filtro_estado in ("inactivo", "inactiva", "false", "0"):
            query = query.filter(Usuario.activo.is_(False))

        # 4. Ordenamiento
        orden = request.args.get("orden", "fecha_desc").strip().lower()
        if orden == "usuario_asc":
            query = query.order_by(Usuario.nombre_usuario.asc())
        elif orden == "usuario_desc":
            query = query.order_by(Usuario.nombre_usuario.desc())
        elif orden == "nombre_asc":
            query = query.order_by(
                func.coalesce(Estudiante.nombre, TutorDocente.nombre, SupervisorInstitucional.nombre, Usuario.nombre_usuario).asc()
            )
        elif orden == "fecha_asc":
            query = query.order_by(Usuario.fecha_creacion.asc(), Usuario.id_usuario.asc())
        else:  # 'fecha_desc' por defecto
            query = query.order_by(Usuario.fecha_creacion.desc(), Usuario.id_usuario.desc())

        # 5. Paginación de SQLAlchemy
        paginacion = query.paginate(page=page, per_page=per_page, error_out=False)

        usuarios_serializados = [u.to_dict() for u in paginacion.items]

        return jsonify({
            "success": True,
            "usuarios": usuarios_serializados,
            "total": paginacion.total,
            "pagina": paginacion.page,
            "paginas": paginacion.pages,
            "por_pagina": paginacion.per_page,
            "hay_siguiente": paginacion.has_next,
            "hay_previo": paginacion.has_prev,
        }), 200

    except Exception as err:
        return jsonify({
            "success": False,
            "message": f"Error interno al consultar usuarios: {str(err)}"
        }), 500


@admin_bp.route("/usuarios/<int:id_usuario>", methods=["GET"])
@admin_required
def detalle_usuario(id_usuario: int):
    """Consulta el expediente y detalle completo de un usuario por su ID."""
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    return jsonify({
        "success": True,
        "usuario": usuario.to_dict()
    }), 200


@admin_bp.route("/usuarios/<int:id_usuario>/toggle-activo", methods=["PUT"])
@admin_required
def toggle_estado_usuario(id_usuario: int):
    """Activa o suspende el acceso de un usuario al sistema."""
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    current_user_id = session.get("user_id")
    if usuario.id_usuario == current_user_id:
        return jsonify({
            "success": False,
            "message": "Operación no permitida: No puedes desactivar tu propia cuenta administradora en sesión."
        }), 400

    estado_anterior = bool(usuario.activo)
    payload = request.get_json(silent=True) or {}
    
    if "activo" in payload:
        usuario.activo = bool(payload["activo"])
    else:
        usuario.activo = not usuario.activo

    # Auditoría forense de cambio
    auditoria = AuditoriaCambios(
        tabla_afectada="usuarios",
        operacion="UPDATE",
        registro_id=usuario.id_usuario,
        datos_anteriores={"activo": estado_anterior},
        datos_nuevos={"activo": usuario.activo},
        columnas_modificadas={"activo": [estado_anterior, usuario.activo]},
        id_usuario=current_user_id,
        usuario_bd="Sistema_Admin",
        ip_origen=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else "WebAdmin"
    )
    db.session.add(auditoria)
    db.session.commit()

    nuevo_estado_texto = "Activado" if usuario.activo else "Desactivado / Suspendido"
    return jsonify({
        "success": True,
        "message": f"Usuario '{usuario.nombre_usuario}' {nuevo_estado_texto} exitosamente.",
        "id_usuario": usuario.id_usuario,
        "activo": usuario.activo
    }), 200


@admin_bp.route("/usuarios/<int:id_usuario>/toggle-2fa", methods=["PUT"])
@admin_required
def toggle_2fa_usuario_admin(id_usuario: int):
    """Permite al Administrador activar o desactivar la verificación en 2 pasos de un usuario."""
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

    current_user_id = session.get("user_id")
    estado_anterior = bool(usuario.has_2fa)
    payload = request.get_json(silent=True) or {}

    if "has_2fa" in payload:
        usuario.has_2fa = bool(payload["has_2fa"])
    else:
        usuario.has_2fa = not usuario.has_2fa

    auditoria = AuditoriaCambios(
        tabla_afectada="usuarios",
        operacion="UPDATE",
        registro_id=usuario.id_usuario,
        datos_anteriores={"has_2fa": estado_anterior},
        datos_nuevos={"has_2fa": usuario.has_2fa},
        columnas_modificadas={"has_2fa": [estado_anterior, usuario.has_2fa]},
        id_usuario=current_user_id,
        usuario_bd="Sistema_Admin",
        ip_origen=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else "WebAdmin"
    )
    db.session.add(auditoria)
    db.session.commit()

    nuevo_txt = "activada" if usuario.has_2fa else "desactivada"
    return jsonify({
        "success": True,
        "message": f"Verificación 2FA {nuevo_txt} para el usuario '{usuario.nombre_usuario}'.",
        "id_usuario": usuario.id_usuario,
        "has_2fa": usuario.has_2fa
    }), 200


@admin_bp.route("/usuarios/estadisticas", methods=["GET"])
@admin_required
def estadisticas_usuarios():
    """Retorna totales agrupados por rol y estado para el panel administrativo."""
    total_general = Usuario.query.count()
    activos = Usuario.query.filter_by(activo=True).count()
    inactivos = Usuario.query.filter_by(activo=False).count()

    roles_data = {}
    roles_db = db.session.query(Usuario.rol, func.count(Usuario.id_usuario)).group_by(Usuario.rol).all()
    for rol, count in roles_db:
        roles_data[rol] = count

    return jsonify({
        "success": True,
        "estadisticas": {
            "total": total_general,
            "activos": activos,
            "inactivos": inactivos,
            "por_rol": roles_data
        }
    }), 200
