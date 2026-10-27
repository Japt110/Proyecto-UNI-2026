"""
===============================================================================
EVENTOS-UNI - MIDDLEWARE DE TELEMETRÍA Y AUDITORÍA DE CONSULTAS (REGISTRO_CONSULTAS)
===============================================================================
Registra automáticamente el rendimiento de endpoints, métodos HTTP,
latencia en milisegundos y códigos de respuesta en la entidad RegistroConsulta.
===============================================================================
"""

import time
import uuid
from datetime import datetime, timezone
from flask import request, g, session
from database import db
from models.sync import RegistroConsulta


def audit_before_request():
    """
    Registra el timestamp de inicio para calcular el tiempo de ejecución de la petición.
    """
    g.start_time = time.time()


def audit_after_request(response):
    """
    Calcula la latencia en milisegundos y persiste la telemetría en la tabla registro_consultas.
    Excluye rutas estáticas para evitar sobrecarga de base de datos.
    """
    path = request.path
    if path.startswith("/static/") or path.startswith("/favicon.ico"):
        return response

    if hasattr(g, "start_time"):
        duracion_ms = int((time.time() - g.start_time) * 1000)
    else:
        duracion_ms = 0

    # Inyección de headers de telemetría y seguridad OWASP
    response.headers["X-Response-Time-Ms"] = str(duracion_ms)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Persistencia asíncrona / atómica en registro_consultas
    try:
        usuario_id = session.get("user_id")
        metodo = request.method
        codigo = response.status_code

        # Solo auditar endpoints API o vistas principales
        if path.startswith("/api/") or path in ("/", "/login", "/asistencia", "/rector", "/usuarios", "/crear-actividad", "/detalle-actividad"):
            consulta = RegistroConsulta(
                id=str(uuid.uuid4()),
                usuario_id=usuario_id,
                nodo_cliente_id=None,
                endpoint_consultado=path[:250],
                metodo_http=metodo[:10],
                codigo_respuesta=codigo,
                tiempo_ejecucion_ms=duracion_ms,
                timestamp_accion=datetime.now(timezone.utc).isoformat()
            )
            db.session.add(consulta)
            db.session.commit()
    except Exception:
        # Evitar que un fallo de auditoría rompa la respuesta al cliente
        db.session.rollback()

    return response
