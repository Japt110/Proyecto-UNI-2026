"""Alcance de estudiantes y vistas del modelo actual."""
from flask import request, session, g, jsonify, redirect
from core.security import verify_token_and_restore_session

def enforce_student_scope():
    if request.endpoint == "static":
        return None
    if not (session.get("user_id") or request.headers.get("Authorization") or request.headers.get("X-Session-Token")):
        return None
    if not verify_token_and_restore_session() or g.current_user.rol != "Estudiante":
        return None
    endpoint = request.endpoint or ""
    if endpoint.startswith(("auth_api.", "profile_api.", "catalogos_api.")):
        return None
    if endpoint in {"index", "login", "pasantias", "perfil", "favicon"}:
        return None
    if endpoint == "serve_html" and request.view_args.get("filename") in {"index", "login", "perfil"}:
        return None
    if request.path.startswith("/api/"):
        return jsonify(success=False, message="No tienes permisos para esta operación."), 403
    return redirect("/")
