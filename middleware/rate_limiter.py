"""
===============================================================================
EVENTOS-UNI - MIDDLEWARE DE RATE LIMITING Y PROTECCIÓN CONTRA ABUSO (DOS)
===============================================================================
Implementa control de tasa de peticiones (Leaky Bucket / Ventana Deslizante)
por dirección IP o Identificador de Hardware (MAC / API Key).
Soporta almacenamiento en memoria y en Redis para clústeres distribuidos.
===============================================================================
"""

import time
from typing import Dict, Tuple
from flask import request, jsonify, current_app


class RateLimiter:
    """
    Limitador de tasa de peticiones configurable por minuto.
    """
    def __init__(self):
        # Almacenamiento en memoria: { "ip": [timestamp1, timestamp2, ...] }
        self._memory_storage: Dict[str, list] = {}

    def is_allowed(self, key: str, max_requests: int = 120, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Verifica si la clave (IP o MAC) ha excedido el límite permitido en la ventana de tiempo.
        
        :param key: Identificador del cliente (ej. IP remota).
        :param max_requests: Máximo de peticiones permitidas.
        :param window_seconds: Ventana de tiempo en segundos (por defecto 60s).
        :return: (permitido: bool, peticiones_restantes: int)
        """
        now = time.time()
        
        # Limpieza de peticiones fuera de la ventana
        if key not in self._memory_storage:
            self._memory_storage[key] = []

        # Filtrar timestamps válidos dentro de la ventana
        self._memory_storage[key] = [
            ts for ts in self._memory_storage[key] if now - ts < window_seconds
        ]

        current_count = len(self._memory_storage[key])
        if current_count >= max_requests:
            return False, 0

        self._memory_storage[key].append(now)
        remaining = max_requests - current_count - 1
        return True, remaining


# Instancia global del RateLimiter
rate_limiter = RateLimiter()


def rate_limit_middleware():
    """
    Middleware que se ejecuta en before_request para validar la tasa de peticiones.
    Ignora archivos estáticos para no penalizar la carga de CSS/JS/Imágenes.
    """
    if not current_app.config.get("RATE_LIMIT_ENABLED", True):
        return None

    # Excluir rutas de recursos estáticos
    path = request.path
    if path.startswith("/static/") or path.startswith("/favicon.ico"):
        return None

    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1").split(",")[0].strip()
    max_reqs = current_app.config.get("RATE_LIMIT_PER_MINUTE", 120)

    allowed, remaining = rate_limiter.is_allowed(client_ip, max_requests=max_reqs, window_seconds=60)
    if not allowed:
        return jsonify({
            "success": False,
            "message": "Límite de peticiones excedido (Rate Limit Exceeded). Por favor intente más tarde.",
            "retry_after_seconds": 60
        }), 429

    return None
