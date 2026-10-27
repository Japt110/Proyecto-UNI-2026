"""
===============================================================================
EVENTOS-UNI - API DE CARGA DE ARCHIVOS (`/api/uploads`)
===============================================================================
Endpoint de persistencia híbrida para imágenes de portada de eventos:
- Si `SUPABASE_URL` y `SUPABASE_KEY` están configuradas en el entorno (Producción),
  persiste el archivo en el bucket 'eventos-portadas' de Supabase Storage vía REST,
  retornando una URL pública permanente con CDN global.
- En modo offline / desarrollo local, guarda el archivo en `static/uploads/`
  retornando la URL pública relativa con fallback automático.
===============================================================================
"""

import os
import uuid
import mimetypes
import urllib.request
import urllib.error
from flask import Blueprint, request, jsonify, current_app
from core.security import login_required

uploads_bp = Blueprint("uploads_api", __name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_FILE_SIZE_MB = 5


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _upload_to_supabase_storage(file_bytes: bytes, filename: str, content_type: str) -> str | None:
    """
    Sube un archivo binario a Supabase Storage mediante la API REST oficial.
    Retorna la URL pública permanente del objeto o None si no está configurado o falla.
    """
    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    supabase_key = (
        os.environ.get("SUPABASE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
    )
    bucket = os.environ.get("SUPABASE_BUCKET", "eventos-portadas")

    if not supabase_url or not supabase_key:
        return None

    upload_endpoint = f"{supabase_url}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "apikey": supabase_key,
        "Content-Type": content_type,
        "x-upsert": "true"
    }

    try:
        req = urllib.request.Request(
            upload_endpoint,
            data=file_bytes,
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status in (200, 201):
                return f"{supabase_url}/storage/v1/object/public/{bucket}/{filename}"
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            pass
        current_app.logger.warning(
            f"[Supabase Storage HTTP {e.code}] Fallback a disco local. Detalle: {err_body or e.reason}"
        )
    except Exception as e:
        current_app.logger.warning(f"[Supabase Storage Error] Fallback a disco local. Detalle: {e}")

    return None


@uploads_bp.route("/image", methods=["POST"])
@login_required
def upload_image():
    """
    Sube una imagen con persistencia híbrida:
    1. Si Supabase Storage está configurado, la persiste en la nube (URL global permanente).
    2. En modo local/desconectado, la guarda en static/uploads/ (URL relativa).
    """
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No se recibió ningún archivo"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "message": "Nombre de archivo vacío"}), 400

    if not _allowed_file(file.filename):
        return jsonify({
            "success": False,
            "message": f"Formato no permitido. Formatos válidos: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    # Validar tamaño
    file.seek(0, os.SEEK_END)
    size_bytes = file.tell()
    file.seek(0)
    if size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
        return jsonify({
            "success": False,
            "message": f"El archivo supera el límite de {MAX_FILE_SIZE_MB} MB."
        }), 413

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    content_type = mimetypes.guess_type(file.filename)[0] or f"image/{ext}"

    file_bytes = file.read()

    # 1. Intentar persistencia en Supabase Storage (Producción / Nube)
    supabase_public_url = _upload_to_supabase_storage(file_bytes, unique_filename, content_type)
    if supabase_public_url:
        return jsonify({
            "success": True,
            "url": supabase_public_url,
            "storage": "supabase",
            "message": "Imagen subida exitosamente a Supabase Storage"
        }), 201

    # 2. Fallback a Persistencia en Disco Local (Desarrollo / Docker / Offline)
    uploads_dir = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    save_path = os.path.join(uploads_dir, unique_filename)
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    public_url = f"/static/uploads/{unique_filename}"

    return jsonify({
        "success": True,
        "url": public_url,
        "storage": "local",
        "message": "Imagen subida exitosamente en almacenamiento local"
    }), 201
