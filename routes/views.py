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
from models.perfil_estudiante import (
    Estudiante,
    Matricula,
    TelefonoEstudiante,
    DireccionEstudiante,
    EducacionPreviaEstudiante,
)
from models.catalogos import (
    Pais,
    Etnia,
    Departamento,
    Municipio,
    CentroEducativo,
    Carrera,
    Beca,
)

views_bp = Blueprint("views", __name__)


def _get_perfil_context():
    """Genera el contexto completo del perfil con catálogos y ficha para pre-renderizado instantáneo."""
    user_id = session.get("user_id")
    usuario = Usuario.query.get(user_id) if user_id else None

    # Catálogos completos desde Supabase
    try:
        paises = [(p.id_pais, p.nombre) for p in Pais.query.order_by(Pais.id_pais).all()]
        etnias = [(e.id_etnia, e.nombre) for e in Etnia.query.order_by(Etnia.id_etnia).all()]
        departamentos = [(d.id_departamento, d.nombre) for d in Departamento.query.order_by(Departamento.id_departamento).all()]
        municipios = [(m.id_municipio, m.nombre) for m in Municipio.query.order_by(Municipio.id_municipio).all()]
        municipios_por_departamento = [
            {"id_municipio": m.id_municipio, "id_departamento": m.id_departamento, "nombre": m.nombre}
            for m in Municipio.query.all()
        ]
        centros = [(c.id_centro, c.nombre) for c in CentroEducativo.query.order_by(CentroEducativo.id_centro).all()]
        carreras = [(c.id_carrera, c.nombre) for c in Carrera.query.order_by(Carrera.id_carrera).all()]
        becas = [(b.id_beca, b.nombre) for b in Beca.query.order_by(Beca.id_beca).all()]
    except Exception:
        paises = [(1, "Nicaragua")]
        etnias = [(1, "Mestizo")]
        departamentos = [(1, "Managua"), (2, "León"), (3, "Estelí")]
        municipios = [(1, "Managua")]
        municipios_por_departamento = [{"id_municipio": 1, "id_departamento": 1, "nombre": "Managua"}]
        centros = [(1, "Instituto Maestro Gabriel")]
        carreras = [(1, "Ingeniería de Sistemas")]
        becas = [(1, "Beca de Excelencia Académica")]

    catalogs = {
        "paises": paises,
        "etnias": etnias,
        "departamentos": departamentos,
        "municipios": municipios,
        "municipios_por_departamento": municipios_por_departamento,
        "centros_educativos": centros,
        "carreras": carreras,
        "becas": becas,
    }

    if not usuario:
        empty_profile = {
            "cup": "CUP-PENDIENTE",
            "cedula": "Pendiente",
            "nombre": "",
            "apellido": "",
            "sexo": "Masculino",
            "fecha_nacimiento": "",
            "edad": "",
            "dimension_nacional": "Natural",
            "id_pais_origen": 1,
            "id_etnia": 1,
            "estado_civil": "Soltero",
            "hijos": 0,
            "email": "",
            "telefono": "",
            "tipo_telefono": "Movil",
            "telefono_principal": True,
            "id_departamento": 1,
            "id_municipio": 1,
            "comunidad": "",
            "zona": "Urbano",
            "direccion": "",
            "direccion_principal": True,
            "id_carrera": 1,
            "id_centro_educativo": 1,
            "centro_educativo": "",
            "educacion_tecnica": "",
            "titulo_obtenido": "Bachiller",
            "anio_graduacion": 2021,
            "periodo_academico": "I Semestre 2026",
            "anio": 4,
            "modalidad": "Presencial",
            "turno": "Matutino",
            "grupo_clase": "4M1-CO",
            "id_beca": 1,
            "estado_matricula": "Activa",
            "has_2fa": False,
        }
        return {
            "es_estudiante": False,
            "usuario": {},
            "profile": empty_profile,
            "perfil": empty_profile,
            "documentos": [],
            "catalogs": catalogs,
            "catalogos": catalogs,
        }

    estudiante = Estudiante.query.get(usuario.id_estudiante) if usuario.id_estudiante else None

    if not estudiante:
        admin_profile = {
            "cup": f"#ROL-{usuario.rol}",
            "cedula": "N/A",
            "nombre": usuario.nombre_usuario,
            "apellido": f"({usuario.rol})",
            "sexo": "Otro",
            "fecha_nacimiento": "",
            "edad": "N/A",
            "dimension_nacional": "Natural",
            "id_pais_origen": 1,
            "id_etnia": 1,
            "estado_civil": "Soltero",
            "hijos": 0,
            "email": usuario.email,
            "telefono": "",
            "tipo_telefono": "Movil",
            "telefono_principal": True,
            "id_departamento": 1,
            "id_municipio": 1,
            "comunidad": "Sede Central",
            "zona": "Urbano",
            "direccion": "Campus Central UNI",
            "direccion_principal": True,
            "id_carrera": 1,
            "id_centro_educativo": 1,
            "centro_educativo": "N/A",
            "educacion_tecnica": "N/A",
            "titulo_obtenido": "Personal Institucional",
            "anio_graduacion": 2020,
            "periodo_academico": "Activo 2026",
            "anio": 5,
            "modalidad": "Presencial",
            "turno": "Matutino",
            "grupo_clase": "ADMIN",
            "id_beca": None,
            "estado_matricula": "Activa",
            "has_2fa": bool(getattr(usuario, "has_2fa", False)),
        }
        return {
            "es_estudiante": False,
            "usuario": {
                "id": usuario.id_usuario,
                "username": usuario.nombre_usuario,
                "email": usuario.email,
                "rol": usuario.rol,
                "has_2fa": bool(getattr(usuario, "has_2fa", False)),
            },
            "profile": admin_profile,
            "perfil": admin_profile,
            "documentos": [],
            "catalogs": catalogs,
            "catalogos": catalogs,
        }

    # Datos del estudiante
    telefonos = estudiante.telefonos or []
    direcciones = estudiante.direcciones or []
    educaciones = estudiante.educaciones_previas or []
    docs = [d.to_dict() for d in estudiante.documentos]

    # Teléfono principal o primero
    tel_obj = next((t for t in telefonos if t.es_principal), telefonos[0] if telefonos else None)

    # Dirección principal o primera
    dir_obj = next((d for d in direcciones if d.es_principal), direcciones[0] if direcciones else None)

    # Educación previa más reciente
    ed_obj = educaciones[0] if educaciones else None

    # Matrícula activa o última
    mat_obj = Matricula.query.filter_by(id_estudiante=estudiante.id_estudiante).order_by(Matricula.id_matricula.desc()).first()

    fn_str = estudiante.fecha_nacimiento.strftime("%Y-%m-%d") if estudiante.fecha_nacimiento else ""
    edad_val = estudiante.edad or estudiante.calcular_edad() if estudiante.fecha_nacimiento else ""

    dep_id = dir_obj.municipio.id_departamento if (dir_obj and dir_obj.municipio) else 1
    mun_id = dir_obj.id_municipio if dir_obj else 1

    profile_data = {
        "id_estudiante": estudiante.id_estudiante,
        "cup": estudiante.cup,
        "cedula": estudiante.cedula,
        "nombre": estudiante.nombre,
        "apellido": estudiante.apellido,
        "nombre_completo": f"{estudiante.nombre} {estudiante.apellido}",
        "sexo": estudiante.sexo or "Masculino",
        "fecha_nacimiento": fn_str,
        "edad": edad_val,
        "dimension_nacional": estudiante.dimension_nacional or "Natural",
        "id_pais_origen": estudiante.id_pais_origen or 1,
        "id_etnia": estudiante.id_etnia or 1,
        "estado_civil": estudiante.estado_civil or "Soltero",
        "hijos": estudiante.hijos if estudiante.hijos is not None else 0,
        "email": usuario.email,
        "telefono": tel_obj.numero if tel_obj else "",
        "tipo_telefono": tel_obj.tipo if tel_obj else "Movil",
        "telefono_principal": tel_obj.es_principal if tel_obj else True,
        "id_departamento": dep_id,
        "id_municipio": mun_id,
        "comunidad": dir_obj.comunidad if dir_obj else "",
        "zona": dir_obj.zona if dir_obj else "Urbano",
        "direccion": dir_obj.direccion_domiciliar if dir_obj else "",
        "direccion_principal": dir_obj.es_principal if dir_obj else True,
        "id_carrera": mat_obj.id_carrera if mat_obj else 1,
        "id_centro_educativo": ed_obj.id_centro_educativo if ed_obj else 1,
        "centro_educativo": ed_obj.centro_educativo.nombre if (ed_obj and ed_obj.centro_educativo) else "Instituto Maestro Gabriel",
        "educacion_tecnica": ed_obj.educacion_tecnica if ed_obj else "",
        "titulo_obtenido": ed_obj.titulo_obtenido if ed_obj else "Bachiller en Ciencias y Letras",
        "anio_graduacion": ed_obj.anio_graduacion if ed_obj else 2021,
        "periodo_academico": mat_obj.periodo_academico if mat_obj else "I Semestre 2026",
        "anio": mat_obj.anio_academico if mat_obj else 4,
        "modalidad": mat_obj.modalidad if mat_obj else "Presencial",
        "turno": mat_obj.turno if mat_obj else "Matutino",
        "grupo_clase": mat_obj.grupo_clase if mat_obj else "4M1-CO",
        "id_beca": mat_obj.id_beca if mat_obj else 1,
        "estado_matricula": mat_obj.estado if mat_obj else "Activa",
        "has_2fa": bool(getattr(usuario, "has_2fa", False)),
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
        "profile": profile_data,
        "perfil": profile_data,
        "documentos": docs,
        "catalogs": catalogs,
        "catalogos": catalogs,
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
