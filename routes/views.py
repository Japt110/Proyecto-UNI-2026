from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
    return render_template("index.html")

@views_bp.route("/login")
def login_view():
    return render_template("login.html")

@views_bp.route("/asistencia")
def asistencia_view():
    return render_template("asistencia.html")

@views_bp.route("/crear-actividad")
def crear_actividad_view():
    return render_template("crear-actividad.html")

@views_bp.route("/detalle-actividad")
def detalle_actividad_view():
    return render_template("detalle-actividad.html")

@views_bp.route("/rector")
def rector_view():
    return render_template("rector.html")

@views_bp.route("/usuarios")
def usuarios_view():
    return render_template("usuarios.html")

@views_bp.route("/pasantias")
def pasantias_view():
    return render_template("index.html")

@views_bp.route("/perfil")
def perfil_view():
    return render_template("perfil.html")