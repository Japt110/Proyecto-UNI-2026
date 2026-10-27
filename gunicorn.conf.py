"""
===============================================================================
EVENTOS-UNI - CONFIGURACIÓN DEL SERVIDOR WSGI GUNICORN (PRODUCCIÓN)
===============================================================================
Calibrado para alta concurrencia, bajo consumo de memoria y compatibilidad
con Render, Cloudflare y Nginx API Gateway.
===============================================================================
"""

import os
import multiprocessing

# Dirección y Puerto de Escucha (Adaptable a Render y Docker)
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Modelo de Concurrencia: Workers Híbridos (Procesos + Hilos)
# En Render Starter/Standard: 2-4 workers con 4 hilos por worker
default_workers = int(os.getenv("WEB_CONCURRENCY", min(4, max(2, multiprocessing.cpu_count()))))
workers = int(os.getenv("GUNICORN_WORKERS", default_workers))
threads = int(os.getenv("GUNICORN_THREADS", 4))
worker_class = "gthread"

# Timeouts y Gestión de Conexiones
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 50))

# Logging Centralizado (Salida estándar stdout/stderr para agregadores de logs)
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Formato de Logs de Acceso
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" (%(D)s µs)'

# Precarga de Aplicación para optimizar memoria RAM (Copy-on-Write)
preload_app = False
