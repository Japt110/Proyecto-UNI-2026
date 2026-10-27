# ===============================================================================
# EVENTOS-UNI - DOCKERFILE DE PRODUCCIÓN MULTI-STAGE
# Imagen optimizada y securizada para Render, Kubernetes y Docker Compose
# ===============================================================================

FROM python:3.13-slim AS base

# Variables de entorno de Python para producción
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=5000

WORKDIR /app

# Instalar dependencias nativas del sistema necesarias para PostgreSQL y Networking
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------------------------------
# Stage de Dependencias
# -------------------------------------------------------------------------------
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y gcc libpq-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------------------------------
# Copia del Código Fuente de la Aplicación
# -------------------------------------------------------------------------------
COPY . .

# Crear usuario sin privilegios para ejecución segura (OWASP Container Security)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/static/uploads /app/instance && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

# Healthcheck para verificar liveness del contenedor
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/favicon.ico || exit 1

# Servidor WSGI Gunicorn optimizado
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
