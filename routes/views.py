"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - RUTAS DE VISTAS WEB
===============================================================================
Sirve las plantillas HTML activas del sistema:
- / y /index     : Catálogo y Bolsa de Trabajo de Pasantías (Interactiva CRUD)
- /login         : Autenticación, Registro y Verificación 2FA
- /register      : Redirección a Registro
- /perfil        : Ficha Socio-Académica y Perfil del Estudiante (CU-01 Pre-renderizada)
- /pasantias     : Alias del Catálogo de Pasantías
===============================================================================
"""

from flask import Blueprint, render_template, session
from core.security import login_required, admin_required
from models.usuarios_auditoria import Usuario
from models.perfil_estudiante import Estudiante, Matricula

views_bp = Blueprint("views", __name__)


def _get_perfil_context():
    """Genera el contexto completo del perfil para pre-renderizado instantáneo en servidor."""
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id) if user_id else None
    if not usuario:
        return {"es_estudiante": False, "usuario": {}, "perfil": {}, "documentos": []}

    estudiante = Estudiante.query.get(usuario.id_estudiante) if usuario.id_estudiante else None

    if not estudiante:
        return {
            "es_estudiante": False,
            "usuario": {
                "id": usuario.id_usuario,
                "username": usuario.nombre_usuario,
                "email": usuario.email,
                "rol": usuario.rol,
                "has_2fa": bool(getattr(usuario, "has_2fa", False)),
            },
            "perfil": {
                "cup": f"#ROL {usuario.rol}",
                "cedula": "N/A",
                "nombre": usuario.nombre_usuario,
                "apellido": f"({usuario.rol})",
                "email": usuario.email,
                "has_2fa": bool(getattr(usuario, "has_2fa", False)),
                "carrera": "Personal Institucional",
                "anio_academico": "Personal Institucional",
                "matricula_estado": "Activo",
                "matricula_periodo": "Activo 2026",
                "beca": "N/A",
                "telefono_principal": "N/A",
                "departamento_principal": "Managua",
                "municipio_principal": "Managua",
                "direccion_principal": "Campus Central UNI",
            },
            "documentos": [],
        }

    matricula_activa = Matricula.query.filter_by(
        id_estudiante=estudiante.id_estudiante,
        estado="Activa"
    ).order_by(Matricula.id_matricula.desc()).first()

    telefonos = estudiante.telefonos or []
    direcciones = estudiante.direcciones or []
    docs = [d.to_dict() for d in estudiante.documentos]

    perfil = {
        "id_estudiante": estudiante.id_estudiante,
        "cup": estudiante.cup,
        "cedula": estudiante.cedula,
        "nombre": estudiante.nombre,
        "apellido": estudiante.apellido,
        "nombre_completo": f"{estudiante.nombre} {estudiante.apellido}",
        "email": usuario.email,
        "carrera": matricula_activa.carrera.nombre if matricula_activa and matricula_activa.carrera else "Ingeniería de Sistemas",
        "anio_academico": matricula_activa.anio_academico if matricula_activa else 4,
        "matricula_estado": matricula_activa.estado if matricula_activa else "Activa",
        "matricula_periodo": matricula_activa.periodo_academico if matricula_activa else "I Semestre 2026",
        "beca": matricula_activa.beca.nombre if matricula_activa and matricula_activa.beca else "Sin Beca",
        "telefono_principal": telefonos[0].numero if telefonos else "",
        "departamento_principal": direcciones[0].municipio.departamento.nombre if direcciones and direcciones[0].municipio and direcciones[0].municipio.departamento else "Managua",
        "municipio_principal": direcciones[0].municipio.nombre if direcciones and direcciones[0].municipio else "Managua",
        "direccion_principal": direcciones[0].direccion_domiciliar if direcciones else "",
    }

    return {
        "es_estudiante": True,
        "usuario": {
            "id": usuario.id_usuario,
            "username": usuario.nombre_usuario,
            "email": usuario.email,
            "rol": usuario.rol,
            "has_2fa": bool(getattr(usuario, "has_2fa", False)),
        },
        "perfil": {
            **perfil,
            "has_2fa": bool(getattr(usuario, "has_2fa", False)),
        },
        "documentos": docs,
    }


@views_bp.route("/")
@views_bp.route("/index")
@login_required
def index():
    """Catálogo y Bolsa de Trabajo de Pasantías con CRUD interactivo."""
    return render_template("index.html")


@views_bp.route("/login")
def login_view():
    """Vista pública de autenticación de usuario (Login / 2FA)."""
    return render_template("login.html")


@views_bp.route("/register")
def register_view():
    """Vista pública de registro de estudiantes y empresas."""
    return render_template("login.html")


@views_bp.route("/pasantias")
@login_required
def pasantias_view():
    """Catálogo de Ofertas de Pasantía."""
    return render_template("index.html")


@views_bp.route("/perfil")
@login_required
def perfil_view():
    """Vista de Perfil Socio-Académico del Estudiante (CU-01) pre-renderizada al instante."""
    ctx = _get_perfil_context()
    return render_template("perfil.html", **ctx)


@views_bp.route("/admin/usuarios")
@admin_required
def admin_usuarios_view():
    """Vista de gestión, visualización y filtrado de usuarios para Administradores."""
    return render_template("admin_usuarios.html")
