"""
===============================================================================
EVENTOS-UNI - SISTEMA DE GESTIÓN DE EVENTOS Y ASISTENCIA UNIVERSITARIA
===============================================================================
Archivo Principal de Inicialización del Servidor Backend (Flask Application Factory)

Este módulo implementa el patrón Application Factory (`create_app`), encargándose de:
1. Configuración de parámetros de entorno y seguridad mediante `Config`.
2. Inicialización del ORM SQLAlchemy y creación de esquemas relacionales.
3. Registro de Blueprints para la API REST y servidor de vistas Jinja2.
===============================================================================
"""

from flask import Flask, render_template
from config import Config
from database import db
from extensions import cache
from routes import (
    auth_bp,
    eventos_bp,
    asistencia_bp,
    stats_bp,
    catalogos_bp,
    uploads_bp,
    views_bp,
    sync_bp,
)


def create_app() -> Flask:
    """
    Fábrica de Aplicación Flask.
    Inicializa configuraciones, extensiones, bases de datos y registra los blueprints.
    
    :return: Instancia configurada de Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # -------------------------------------------------------------------------
    # 1. Inicialización de Extensiones (SQLAlchemy y Flask-Caching)
    # -------------------------------------------------------------------------
    db.init_app(app)
    cache.init_app(app)

    # -------------------------------------------------------------------------
    # 2. Registro de Blueprints API RESTful
    # -------------------------------------------------------------------------
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(eventos_bp, url_prefix="/api/eventos")
    app.register_blueprint(asistencia_bp, url_prefix="/api/asistencia")
    app.register_blueprint(stats_bp, url_prefix="/api/stats")
    app.register_blueprint(catalogos_bp, url_prefix="/api/catalogos")
    app.register_blueprint(uploads_bp, url_prefix="/api/uploads")
    app.register_blueprint(views_bp, url_prefix="/api/views")
    app.register_blueprint(sync_bp, url_prefix="/api/v1")

    # -------------------------------------------------------------------------
    # 3. Creación Automática de Tablas en BD Local (Modo Offline-First)
    # -------------------------------------------------------------------------
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            # En clústeres de producción (PostgreSQL/Supabase) el esquema ya existe vía DDL
            pass

    # -------------------------------------------------------------------------
    # 4. Registro de Middlewares de Perímetro, Seguridad y Telemetría
    # -------------------------------------------------------------------------
    from middleware import (
        rate_limit_middleware,
        audit_before_request,
        audit_after_request,
        validate_request_payload,
    )

    @app.before_request
    def run_before_request_middlewares():
        audit_before_request()
        
        # Validar payload entrante
        val_res = validate_request_payload()
        if val_res is not None:
            return val_res

        # Rate Limiting
        rate_res = rate_limit_middleware()
        if rate_res is not None:
            return rate_res

    @app.after_request
    def run_after_request_middlewares(response):
        # Inyectar version hash de semilla si existe
        try:
            import os
            seed_file = os.path.join(app.instance_path, "db_seed.id")
            if os.path.exists(seed_file):
                with open(seed_file, "r") as f:
                    response.headers["X-DB-Seed"] = f.read().strip()
        except Exception:
            pass

        # Telemetría y headers de seguridad OWASP
        return audit_after_request(response)

    # -------------------------------------------------------------------------
    # 4. Rutas Directas de Vistas HTML (Interfaz Web Vanilla JS)
    # -------------------------------------------------------------------------

    @app.route('/')
    def index():
        """Página principal - Dashboard de Mis Actividades (Encargado)"""
        return render_template('index.html')

    @app.route('/login')
    def login():
        """Vista de Autenticación de Usuario"""
        return render_template('login.html')

    @app.route('/asistencia')
    def asistencia():
        """Vista de Registro y Toma de Asistencia (Escáner/Manual)"""
        return render_template('asistencia.html')

    @app.route('/crear-actividad')
    def crear_actividad():
        """Formulario de Registro de Nuevas Actividades Institucionales"""
        return render_template('crear-actividad.html')

    @app.route('/detalle-actividad')
    def detalle_actividad():
        """Vista Detallada y Edición de una Actividad"""
        return render_template('detalle-actividad.html')

    @app.route('/rector')
    def rector():
        """Dashboard General de Estadísticas e Indicadores (Rector)"""
        return render_template('rector.html')

    @app.route('/usuarios')
    def usuarios():
        """Gestión y Consulta del Padrón Universitario"""
        return render_template('usuarios.html')

    @app.route('/favicon.ico')
    def favicon():
        """Manejador de favicon para prevenir peticiones 404 innecesarias"""
        return '', 204

    @app.route('/<path:filename>.html')
    def serve_html(filename: str):
        """Manejador dinámico de compatibilidad para URLs con extensión .html"""
        return render_template(f'{filename}.html')

    return app


# Instancia para ejecución directa o servidores WSGI / Gunicorn / Waitress
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)