"""Aplicación UNI conectada al modelo socioacadémico vigente."""
from flask import Flask, render_template, request, redirect, g, jsonify
from config import Config
from database import db
from extensions import cache
from routes import auth_bp, catalogos_bp, profile_bp
import models


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)
    db.init_app(app)
    cache.init_app(app)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(catalogos_bp, url_prefix="/api/catalogos")
    app.register_blueprint(profile_bp, url_prefix="/api/perfil")

    # Producción/local: migraciones explícitas. Nunca crear tablas silenciosamente al arrancar.
    if app.testing:
        from core.schema_rules import install_schema_rules
        with app.app_context():
            db.create_all()
            with db.engine.begin() as connection:
                install_schema_rules(connection)

    from middleware import audit_before_request, audit_after_request, validate_request_payload, rate_limit_middleware
    from core.security import verify_token_and_restore_session
    from core.access_policy import enforce_student_scope

    @app.before_request
    def before_request():
        audit_before_request()
        for check in (validate_request_payload, rate_limit_middleware, enforce_student_scope):
            result = check()
            if result is not None:
                return result
        if request.endpoint in {"index", "pasantias", "perfil", "serve_html"}:
            if request.endpoint == "serve_html" and request.view_args.get("filename") == "login":
                return None
            if not verify_token_and_restore_session():
                return redirect("/login")

    @app.after_request
    def after_request(response):
        if response.mimetype == "text/html" or request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return audit_after_request(response)

    @app.context_processor
    def authenticated_viewer():
        user = getattr(g, "current_user", None)
        return dict(viewer_role=user.rol if user else "",
                    viewer_is_admin=bool(user and user.rol in ("Administrador", "Coordinador")),
                    viewer_name=user.nombre_visible if user else "",
                    viewer_code=user.estudiante.cup if user and user.estudiante else "")

    @app.route("/")
    @app.route("/api/views/")
    def index():
        return render_template("index.html")

    @app.route("/login")
    @app.route("/api/views/login")
    def login():
        return render_template("login.html")

    @app.route("/pasantias")
    @app.route("/api/views/pasantias")
    def pasantias():
        return render_template("index.html")

    @app.route("/perfil")
    @app.route("/api/views/perfil")
    def perfil():
        from routes.profile_api import profile_data, profile_options
        profile = profile_data(g.current_user)
        return render_template("perfil.html", profile=profile, catalogs=profile_options(profile))

    @app.route("/favicon.ico")
    def favicon():
        return "", 204

    @app.route("/<path:filename>.html")
    def serve_html(filename):
        if filename == "perfil":
            return perfil()
        if filename in {"index", "login"}:
            return render_template(filename + ".html")
        return jsonify(success=False, message="Esta vista pertenece al modelo de eventos anterior."), 410

    @app.route("/api/<path:legacy>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def retired_api(legacy):
        if not verify_token_and_restore_session():
            return jsonify(success=False, message="Se requiere iniciar sesión."), 401
        prefixes = ("eventos", "asistencia", "stats", "v1/", "uploads", "views/")
        if legacy.startswith(prefixes):
            return jsonify(success=False, message="Esta operación pertenece al esquema de eventos anterior y no está disponible en el modelo de pasantías."), 410
        return jsonify(success=False, message="Ruta no encontrada."), 404

    return app


app = create_app()
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
