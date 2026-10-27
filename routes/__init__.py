"""
Módulo de Rutas y Controladores API REST / Vistas
Eventos-UNI - Sistema de Gestión de Eventos
"""

from routes.views import views_bp
from routes.auth_api import auth_bp
from routes.eventos_api import eventos_bp
from routes.asistencia_api import asistencia_bp
from routes.stats_api import stats_bp
from routes.catalogos_api import catalogos_bp
from routes.uploads_api import uploads_bp
from routes.sync_api import sync_bp

__all__ = [
    "views_bp",
    "auth_bp",
    "eventos_bp",
    "asistencia_bp",
    "stats_bp",
    "catalogos_bp",
    "uploads_bp",
    "sync_bp",
]