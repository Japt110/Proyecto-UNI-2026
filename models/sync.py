"""
===============================================================================
EVENTOS-UNI - MODELOS DE SINCRONIZACIÓN DISTRIBUIDA, AUDITORÍA Y TELEMETRÍA (5FN)
===============================================================================
Define las 6 entidades ORM del Clúster Central (PostgreSQL / Supabase):
- NodoCliente: Registro y autenticación de terminales de campo (escáneres / clientes offline).
- LoteSincronizacion: Control de paquetes batch recibidos desde terminales.
- ConflictoSincronizacion: Colisiones concurrentes de datos con payloads JSON.
- BitacoraAccion: Auditoría forense inmutable con snapshots de datos previos y nuevos.
- Tombstone: Marcadores de eliminación física/lógica para propagación a clientes offline.
- RegistroConsulta: Telemetría y monitoreo de rendimiento de endpoints HTTP/API.
===============================================================================
"""

import uuid
from datetime import datetime, timezone
from database import db


# -----------------------------------------------------------------------------
# 1. Entidad: Nodo Cliente (Terminal de Campo / Dispositivo Desconectado)
# -----------------------------------------------------------------------------

class NodoCliente(db.Model):
    """
    Modelo ORM que identifica a una terminal o equipo de campo autorizado
    para operar con base de datos local (SQLite) y sincronizar hacia el clúster central.
    """
    __tablename__ = "nodos_cliente"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sede_id = db.Column(db.String(36), db.ForeignKey("sedes.id"), nullable=False, index=True)
    nombre_equipo = db.Column(db.String(100), nullable=False)
    mac_adress = db.Column(db.String(50), nullable=False, unique=True, index=True)  # MAC Address de la terminal
    api_key_hash = db.Column(db.String(255), nullable=False)                         # Hash de la API Key para handshake
    estado_activo = db.Column(db.Boolean, nullable=False, default=True)
    ultima_sincronizacion = db.Column(db.String(50), nullable=True)                  # ISO 8601 UTC

    # Relaciones relacionales
    sede = db.relationship("Sede", backref="nodos_cliente")
    lotes = db.relationship("LoteSincronizacion", backref="nodo_cliente", cascade="all, delete-orphan")
    tombstones = db.relationship("Tombstone", backref="nodo_cliente")
    consultas = db.relationship("RegistroConsulta", backref="nodo_cliente")


# -----------------------------------------------------------------------------
# 2. Entidad: Lote de Sincronización (Batch Transaccional)
# -----------------------------------------------------------------------------

class LoteSincronizacion(db.Model):
    """
    Modelo ORM que agrupa y audita un paquete de eventos o registros
    transmitido por un nodo de campo durante el proceso de reconexión.
    """
    __tablename__ = "lotes_sincronizacion"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nodos_cliente_id = db.Column(db.String(36), db.ForeignKey("nodos_cliente.id", ondelete="CASCADE"), nullable=False, index=True)
    tabla_afectada = db.Column(db.String(50), nullable=True)                        # ej. 'asistencias', 'actividades', 'multiple'
    total_registros = db.Column(db.Integer, nullable=False, default=0)
    timestamp_recepcion = db.Column(db.String(50), nullable=False, default=lambda: datetime.now(timezone.utc).isoformat())
    estado_procesamiento = db.Column(db.String(30), nullable=False, default="PENDIENTE")  # 'PENDIENTE', 'PROCESADO', 'ERROR', 'CON_CONFLICTOS'

    # Relaciones relacionales
    conflictos = db.relationship("ConflictoSincronizacion", backref="lote", cascade="all, delete-orphan")


# -----------------------------------------------------------------------------
# 3. Entidad: Conflicto de Sincronización (Colisiones Concurrentes)
# -----------------------------------------------------------------------------

class ConflictoSincronizacion(db.Model):
    """
    Modelo ORM que almacena discrepancias de versión detectadas durante la reconciliación
    UPSERT entre la copia local de un nodo y la fuente de verdad central.
    """
    __tablename__ = "conflictos_sincronizacion"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lote_id = db.Column(db.String(36), db.ForeignKey("lotes_sincronizacion.id", ondelete="CASCADE"), nullable=False, index=True)
    tabla_afectada = db.Column(db.String(50), nullable=False)
    registro_id_conflicto = db.Column(db.String(36), nullable=False, index=True)
    tipo_conflicto = db.Column(db.String(50), nullable=False)                       # 'VERSION_CONCURRENTE', 'FK_NO_ENCONTRADA', 'ELIMINACION_CONCURRENTE'
    payload_local = db.Column(db.JSON, nullable=False)                               # Snapshot JSON recibido del cliente
    payload_servidor = db.Column(db.JSON, nullable=True)                            # Snapshot JSON existente en servidor
    estado_resolucion = db.Column(db.String(30), nullable=False, default="PENDIENTE") # 'PENDIENTE', 'RESUELTO_LOCAL', 'RESUELTO_SERVIDOR', 'RESUELTO_MANUAL'
    resuelto_por_usuario_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=True)

    # Relaciones relacionales
    resuelto_por = db.relationship("Usuario", backref="conflictos_resueltos")


# -----------------------------------------------------------------------------
# 4. Entidad: Bitácora de Acciones (Auditoría Forense Inmutable)
# -----------------------------------------------------------------------------

class BitacoraAccion(db.Model):
    """
    Modelo ORM para trazabilidad y auditoría forense de todas las operaciones
    críticas efectuadas en la plataforma (cambios de estado, bajas, actualizaciones).
    """
    __tablename__ = "bitacoras_acciones"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=True, index=True)
    direccion_ip = db.Column(db.String(50), nullable=False, default="127.0.0.1")
    accion_realizada = db.Column(db.String(100), nullable=False)                    # ej. 'CREAR_ACTIVIDAD', 'UPSERT_ASISTENCIA', 'ELIMINAR_EVENTO'
    tabla_afectada = db.Column(db.String(50), nullable=False)
    registro_id_afectado = db.Column(db.String(36), nullable=True, index=True)
    datos_previos = db.Column(db.JSON, nullable=True)                               # JSONB del estado anterior
    datos_nuevos = db.Column(db.JSON, nullable=True)                                # JSONB del estado resultante
    timestamp_accion = db.Column(db.String(50), nullable=False, default=lambda: datetime.now(timezone.utc).isoformat())

    # Relaciones relacionales
    usuario = db.relationship("Usuario", backref="bitacoras_acciones")


# -----------------------------------------------------------------------------
# 5. Entidad: Tombstones (Marcadores de Registro Eliminado)
# -----------------------------------------------------------------------------

class Tombstone(db.Model):
    """
    Modelo ORM que almacena las eliminaciones físicas/lógicas para asegurar que
    los nodos desconectados propaguen la baja al reconectarse sin revivir registros borrados.
    """
    __tablename__ = "tombstones"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tabla_afectada = db.Column(db.String(50), nullable=False)
    registro_id_eliminado = db.Column(db.String(36), nullable=False, index=True)
    timestamp_eliminacion = db.Column(db.String(50), nullable=False, default=lambda: datetime.now(timezone.utc).isoformat())
    usuario_elimino_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=True)
    nodo_cliente_id = db.Column(db.String(36), db.ForeignKey("nodos_cliente.id"), nullable=True)

    # Relaciones relacionales
    usuario_elimino = db.relationship("Usuario", backref="tombstones_registrados")


# -----------------------------------------------------------------------------
# 6. Entidad: Registro de Consultas (Telemetría y Métricas de Rendimiento)
# -----------------------------------------------------------------------------

class RegistroConsulta(db.Model):
    """
    Modelo ORM para monitoreo de tráfico, auditoría de endpoints consultados,
    tiempos de ejecución y estados HTTP procesados por el backend.
    """
    __tablename__ = "registro_consultas"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=True, index=True)
    nodo_cliente_id = db.Column(db.String(36), db.ForeignKey("nodos_cliente.id"), nullable=True, index=True)
    endpoint_consultado = db.Column(db.String(255), nullable=False)
    metodo_http = db.Column(db.String(10), nullable=False)                          # GET, POST, PUT, DELETE, PATCH
    codigo_respuesta = db.Column(db.Integer, nullable=False)                        # 200, 201, 400, 401, 403, 409, 500
    tiempo_ejecucion_ms = db.Column(db.Integer, nullable=False, default=0)
    timestamp_accion = db.Column(db.String(50), nullable=False, default=lambda: datetime.now(timezone.utc).isoformat())

    # Relaciones relacionales
    usuario = db.relationship("Usuario", backref="consultas_realizadas")
