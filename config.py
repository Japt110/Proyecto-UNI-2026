"""
===============================================================================
EVENTOS-UNI - CONFIGURACIÓN DEL SISTEMA BACKEND (LOCAL / RENDER / SUPABASE)
===============================================================================
Módulo centralizado de parámetros de configuración, políticas de seguridad OWASP,
pool de conexiones PostgreSQL (Supabase / Render) y backend de sesiones/caché Redis.
===============================================================================
"""

import os
from datetime import timedelta


def _normalize_database_url(url: str) -> str:
    """
    Normaliza el esquema de conexión para compatibilidad con SQLAlchemy 2.0.
    Reemplaza 'postgres://' por 'postgresql://' (formato estándar de psycopg2/psycopg3).
    """
    if not url:
        return url
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    """
    Clase de Configuración Base para Flask.
    Soporta operación local con SQLite y despliegue en la nube con Supabase / Render / Redis.
    """
    # -------------------------------------------------------------------------
    # 1. Modo de Ejecución y Clave Secreta Criptográfica (OWASP)
    # -------------------------------------------------------------------------
    ENV = os.getenv("FLASK_ENV", "production" if os.getenv("RENDER") else "development")
    DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY", "eventos-uni-secret-key-permanente-2026-production-v1")

    # -------------------------------------------------------------------------
    # 2. Persistencia Principal: PostgreSQL (Supabase / Render) o SQLite Local
    # -------------------------------------------------------------------------
    _BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    _DEFAULT_DB_PATH = os.path.join(_BASE_DIR, "app_local.db").replace("\\", "/")
    
    _RAW_DB_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL") or f"sqlite:///{_DEFAULT_DB_PATH}"
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(_RAW_DB_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de Pool de Conexiones optimizado para Supabase (Supavisor / Direct)
    if "sqlite" in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(os.getenv("DB_POOL_SIZE", 10)),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 20)),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", 30)),
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", 1800)),
            "pool_pre_ping": True,  # Verifica liveness de conexión antes de usarla (Vital para Supabase)
        }

    # Réplica de Lectura Opcional (Read Replica Splitting)
    _READ_DB_URL = os.getenv("DATABASE_READ_URL")
    if _READ_DB_URL:
        SQLALCHEMY_BINDS = {
            "read_replica": _normalize_database_url(_READ_DB_URL)
        }

    # -------------------------------------------------------------------------
    # 3. Hardening y Seguridad de Cookies de Sesión (Mitigación XSS / CSRF)
    # -------------------------------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True          # Inaccesible desde scripts JavaScript del cliente (Anti-XSS)
    SESSION_COOKIE_SAMESITE = "Lax"         # Restringe envío de cookies en peticiones cruzadas (Anti-CSRF)
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0").lower() in ("1", "true", "yes") or bool(os.getenv("RENDER"))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # Duración de la sesión laboral

    # -------------------------------------------------------------------------
    # 4. Restricciones de Carga y Payload (Protección contra DoS / Inundación)
    # -------------------------------------------------------------------------
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # Tamaño máximo de payload: 16 Megabytes

    # -------------------------------------------------------------------------
    # 5. Caché Centralizado y Sesiones Distribuidas (Redis / SimpleCache)
    # -------------------------------------------------------------------------
    REDIS_URL = os.getenv("REDIS_URL")
    if REDIS_URL:
        CACHE_TYPE = "RedisCache"
        CACHE_REDIS_URL = REDIS_URL
        CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
        # Configuración de Sesiones en Redis si Flask-Session está habilitado
        SESSION_TYPE = "redis"
        SESSION_REDIS_URL = REDIS_URL
    else:
        CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
        CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
        SESSION_TYPE = None

    # -------------------------------------------------------------------------
    # 6. Parámetros del Perímetro de Red y Rate Limiting
    # -------------------------------------------------------------------------
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ("1", "true", "yes")
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 120))