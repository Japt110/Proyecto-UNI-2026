"""
===============================================================================
EVENTOS-UNI - MODELOS DE ACTIVIDADES, LINEAMIENTOS Y MARCAS DE ASISTENCIA
===============================================================================
Define las entidades transaccionales del dominio de eventos:
- Actividad: Evento o proyecto científico organizado por la universidad.
- ActividadLineamiento: Asociación N:M entre Actividad y Lineamiento con justificación.
- Asistencia: Registro individual de presencia de una Persona en una Actividad.
Soporta banderas de sincronización offline (`is_synced`, `created_offline`).
===============================================================================
"""

import uuid
from datetime import datetime, timezone
from database import db


# -----------------------------------------------------------------------------
# 1. Entidad Transaccional: Actividad / Evento Institucional
# -----------------------------------------------------------------------------

class Actividad(db.Model):
    """
    Modelo ORM que representa un evento, taller, simposio o feria científica
    registrado en la plataforma.
    """
    __tablename__ = "actividades"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo_actividad = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    tipo_actividad_id = db.Column(db.String(36), db.ForeignKey("tipos_actividad.id"), nullable=False)
    unidad_responsable_id = db.Column(db.String(36), db.ForeignKey("unidades_organizativas.id"), nullable=False)
    usuario_creador_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    espacio_fisico_id = db.Column(db.String(36), db.ForeignKey("espacios_fisicos.id"), nullable=False)
    proposito = db.Column(db.Text, nullable=True)
    imagen_url = db.Column(db.String(500), nullable=True)  # Ruta relativa: /static/uploads/<filename>

    # Fechas y Horarios en cadenas ISO 8601 (Compatibles con SQLite y PostgreSQL)
    fecha_inicio = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    fecha_fin = db.Column(db.String(10), nullable=False)     # YYYY-MM-DD
    hora_inicio = db.Column(db.String(8), nullable=False)    # HH:MM:SS
    hora_fin = db.Column(db.String(8), nullable=False)       # HH:MM:SS

    # Banderas de Sincronización, Auditoría Offline y Estado de Asistencia
    asistencia_abierta = db.Column(db.Boolean, nullable=False, default=True)   # True: asistencias permitidas, False: cerradas
    is_synced = db.Column(db.Integer, nullable=False, default=0, index=True)  # 0: Pendiente, 1: Sincronizado
    created_offline = db.Column(db.Integer, nullable=False, default=0)         # 0: En línea, 1: Creado offline
    updated_at = db.Column(db.String(50), nullable=False, default=lambda: datetime.now(timezone.utc).isoformat())

    # Relaciones relacionales
    asistencias = db.relationship("Asistencia", backref="actividad", cascade="all, delete-orphan")
    creador = db.relationship("Usuario", backref="actividades_creadas")
    lineamientos_asociados = db.relationship("ActividadLineamiento", backref="actividad", cascade="all, delete-orphan")

    def calcular_status(self) -> str:
        """
        Calcula dinámicamente el estado temporal de la actividad
        comparando la fecha de fin e inicio contra la fecha local/UTC actual.
        Tolerante a tipos datetime.date y cadenas ISO 'YYYY-MM-DD'.
        
        :return: 'pasados', 'programados' o 'activos'.
        """
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        f_fin = str(self.fecha_fin) if self.fecha_fin is not None else ""
        f_ini = str(self.fecha_inicio) if self.fecha_inicio is not None else ""

        if f_fin and f_fin < hoy_str:
            return "pasados"
        elif f_ini and f_ini > hoy_str:
            return "programados"
        else:
            return "activos"


# -----------------------------------------------------------------------------
# 2. Entidad Intermedia: Marcado de Lineamientos Estratégicos (N:M con Justificación)
# -----------------------------------------------------------------------------

class ActividadLineamiento(db.Model):
    """
    Modelo ORM que relaciona una Actividad con un Lineamiento Estratégico,
    permitiendo registrar la justificación/aporte específico (máximo 4 lineamientos por evento).
    """
    __tablename__ = "actividades_lineamientos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actividad_id = db.Column(db.String(36), db.ForeignKey("actividades.id", ondelete="CASCADE"), nullable=False)
    lineamiento_id = db.Column(db.String(36), db.ForeignKey("lineamientos.id", ondelete="CASCADE"), nullable=False)
    justificacion = db.Column(db.Text, nullable=True)

    # Relación al Lineamiento
    lineamiento = db.relationship("Lineamiento", backref="actividades_asociadas")


# -----------------------------------------------------------------------------
# 3. Entidad Transaccional: Registro de Asistencia
# -----------------------------------------------------------------------------

class Asistencia(db.Model):
    """
    Modelo ORM que almacena la confirmación atómica de asistencia de una Persona
    a una Actividad específica.
    """
    __tablename__ = "asistencias"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actividad_id = db.Column(db.String(36), db.ForeignKey("actividades.id", ondelete="CASCADE"), nullable=False)
    persona_id = db.Column(db.String(36), db.ForeignKey("personas.id"), nullable=False)
    usuario_registrador_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    timestamp_registro = db.Column(db.String(50), nullable=False, default=lambda: datetime.now(timezone.utc).isoformat())

    # Estado de Sincronización
    is_synced = db.Column(db.Integer, nullable=False, default=0, index=True)

    # Relaciones relacionales
    registrador = db.relationship("Usuario", backref="asistencias_registradas")