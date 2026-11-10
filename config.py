"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - CONFIGURACIÓN MODULAR DEL BACKEND
===============================================================================
Módulo centralizado de parámetros de configuración y variables de entorno (.env):
- Políticas de seguridad OWASP y claves criptográficas.
- Persistencia de base de datos relacional (PostgreSQL / SQLite).
- Motor de correo electrónico transaccional y 2FA (Flask-Mail).
- Parámetros institucionales, reglas de negocio académicas y duraciones de sesión.
===============================================================================
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar automáticamente las variables de entorno desde el archivo .env
load_dotenv()


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
    SECRET_KEY = os.getenv("SECRET_KEY", "pasantias-uni-secret-key-permanente-2026-production-v1")

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
            "pool_pre_ping": True,
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
    
    SECURITY_SESSION_LIFETIME_HOURS = int(os.getenv("SECURITY_SESSION_LIFETIME_HOURS", 8))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=SECURITY_SESSION_LIFETIME_HOURS)
    
    SECURITY_REMEMBER_DAYS = int(os.getenv("SECURITY_REMEMBER_DAYS", 30))
    REMEMBER_COOKIE_DURATION = timedelta(days=SECURITY_REMEMBER_DAYS)

    # -------------------------------------------------------------------------
    # 4. Restricciones de Carga y Payload (Protección contra DoS / Inundación)
    # -------------------------------------------------------------------------
    MAX_CONTENT_LENGTH_MB = int(os.getenv("MAX_CONTENT_LENGTH_MB", 16))
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH_MB * 1024 * 1024

    # -------------------------------------------------------------------------
    # 5. Caché Centralizado y Sesiones Distribuidas (Redis / SimpleCache)
    # -------------------------------------------------------------------------
    REDIS_URL = os.getenv("REDIS_URL")
    if REDIS_URL:
        CACHE_TYPE = "RedisCache"
        CACHE_REDIS_URL = REDIS_URL
        CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
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

    # -------------------------------------------------------------------------
    # 7. Configuración Modular de Correo Electrónico (Flask-Mail / 2FA)
    # -------------------------------------------------------------------------
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() in ("1", "true", "yes")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "notificaciones.pasantias@uni.edu.ni").strip()
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "").strip().replace(" ", "")
    MAIL_SENDER_NAME = os.getenv("MAIL_SENDER_NAME", "Sistema de Control de Pasantías UNI")
    
    # Remitente por defecto (tupla o string RFC 822)
    _custom_sender = os.getenv("MAIL_DEFAULT_SENDER")
    if _custom_sender:
        MAIL_DEFAULT_SENDER = _custom_sender
    else:
        MAIL_DEFAULT_SENDER = (MAIL_SENDER_NAME, MAIL_USERNAME)

    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "false").lower() in ("1", "true", "yes")
    MAIL_ASCII_ATTACHMENTS = False

    # -------------------------------------------------------------------------
    # 8. Identidad Institucional y Branding Modular
    # -------------------------------------------------------------------------
    SYSTEM_NAME = os.getenv("SYSTEM_NAME", "Sistema Web de Control de Pasantías")
    INSTITUTION_NAME = os.getenv("INSTITUTION_NAME", "Universidad Nacional de Ingeniería")
    INSTITUTION_SHORT = os.getenv("INSTITUTION_SHORT", "UNI")
    INSTITUTION_CONTACT_EMAIL = os.getenv("INSTITUTION_CONTACT_EMAIL", "vinculacion@uni.edu.ni")
    INSTITUTION_WEBSITE = os.getenv("INSTITUTION_WEBSITE", "https://www.uni.edu.ni")

    # -------------------------------------------------------------------------
    # 9. Parámetros de Seguridad y 2FA
    # -------------------------------------------------------------------------
    SECURITY_2FA_EXPIRATION_MINUTES = int(os.getenv("SECURITY_2FA_EXPIRATION_MINUTES", 10))

    # -------------------------------------------------------------------------
    # 10. Reglas de Negocio Institucionales (Elegibilidad de Pasantías)
    # -------------------------------------------------------------------------
    ACADEMIC_MIN_YEAR = int(os.getenv("ACADEMIC_MIN_YEAR", 4))
    ACADEMIC_MAX_YEAR = int(os.getenv("ACADEMIC_MAX_YEAR", 5))
    ACADEMIC_REQUIRE_ACTIVE_ENROLLMENT = os.getenv("ACADEMIC_REQUIRE_ACTIVE_ENROLLMENT", "true").lower() in ("1", "true", "yes")
    COMPANY_REQUIRE_APPROVAL = os.getenv("COMPANY_REQUIRE_APPROVAL", "true").lower() in ("1", "true", "yes")
