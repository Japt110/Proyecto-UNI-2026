"""
===============================================================================
EVENTOS-UNI - MIDDLEWARE DE VALIDACIÓN Y SANITIZACIÓN DE ENTRADAS (PERÍMETRO WAF)
===============================================================================
Inspecciona los payloads entrantes contra patrones maliciosos, JSON inválido
o tamaños de cuerpo anómalos antes de que alcancen los controladores de negocio.
===============================================================================
"""

from flask import request, jsonify


def validate_request_payload():
    """
    Inspecciona y valida el payload JSON entrante en métodos POST, PUT y PATCH.
    """
    if request.method in ("POST", "PUT", "PATCH"):
        # Excluir subida de archivos multipart
        if request.path.startswith("/api/uploads/"):
            return None

        # Si el cliente declara contenido JSON pero el cuerpo está vacío o es inválido
        content_type = request.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                # Intentar parsear el JSON
                data = request.get_json(silent=True)
                if data is None and request.get_data(as_text=True).strip():
                    return jsonify({
                        "success": False,
                        "message": "Formato JSON malformado o inválido"
                    }), 400
            except Exception:
                return jsonify({
                    "success": False,
                    "message": "Error al procesar el cuerpo de la petición"
                }), 400

    return None
