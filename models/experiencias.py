"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - SUBDOMINIO D: EXPERIENCIAS
===============================================================================
Modelos ORM relacionales para la gestión de Prácticas y Pasantías:
- Experiencia (experiencias): Supertipo / registro troncal de experiencia formativa
- Practica (practicas): Especialización para Prácticas Profesionales / Pre-profesionales
- Pasantia (pasantias): Especialización para Pasantías
- AsignacionExperiencia (asignaciones_experiencia): Historial de roles de tutores/supervisores
- PlanTrabajo (planes_trabajo): Versiones del plan de trabajo de la experiencia
- ActividadPlan (actividades_plan): Cronograma de actividades del plan
- EntregablePlan (entregables_plan): Productos o entregables requeridos
- HitoPlan (hitos_plan): Puntos de control o hitos calendarizados
- CriterioEvaluacion (criterios_evaluacion): Rúbrica y porcentajes de calificación
- Evaluacion (evaluaciones): Calificaciones emitidas por tutores o supervisores
- Documento (documentos): Evidencias, cartas, convenios e informes respaldatorios
===============================================================================
"""

from datetime import datetime, timezone
from database import db


class Experiencia(db.Model):
    """Troncal de la experiencia formativa (Práctica o Pasantía) realizada por el estudiante."""
    __tablename__ = "experiencias"

    id_experiencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("estudiantes.id_estudiante", ondelete="CASCADE"), nullable=False, index=True)
    tipo_experiencia = db.Column(db.String(30), nullable=False)  # ENUM: 'Practica', 'Pasantia'
    modalidad = db.Column(db.String(30), nullable=False)         # ENUM: 'Presencial', 'Remoto', 'Hibrido'
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=True)
    horas_totales = db.Column(db.Integer, nullable=False, default=0)
    estado = db.Column(db.String(30), nullable=False, default="En_Proceso")  # ENUM: 'Pendiente', 'En_Proceso', 'Aprobada', 'Reprobada', 'Cancelada'
    origen = db.Column(db.String(50), nullable=True)  # ENUM: 'Propuesta_Estudiante', 'Convocatoria_Institucional', 'Convenio'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relación N:1 con Estudiante
    estudiante = db.relationship("Estudiante", back_populates="experiencias")

    # Subtipos 1:1
    practica = db.relationship("Practica", back_populates="experiencia", uselist=False, cascade="all, delete-orphan")
    pasantia = db.relationship("Pasantia", back_populates="experiencia", uselist=False, cascade="all, delete-orphan")

    # Relaciones 1:N
    asignaciones = db.relationship("AsignacionExperiencia", back_populates="experiencia", cascade="all, delete-orphan", lazy="select")
    planes_trabajo = db.relationship("PlanTrabajo", back_populates="experiencia", cascade="all, delete-orphan", lazy="select")
    evaluaciones = db.relationship("Evaluacion", back_populates="experiencia", cascade="all, delete-orphan", lazy="select")
    documentos = db.relationship("Documento", back_populates="experiencia", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return f"<Experiencia id={self.id_experiencia} estudiante_id={self.id_estudiante} tipo='{self.tipo_experiencia}' estado='{self.estado}'>"


class Practica(db.Model):
    """Subtipo 1:1 de Experiencia para Prácticas."""
    __tablename__ = "practicas"

    id_experiencia = db.Column(
        db.Integer,
        db.ForeignKey("experiencias.id_experiencia", ondelete="CASCADE"),
        primary_key=True,
    )
    etapa = db.Column(db.String(50), nullable=False)  # ENUM: ej. 'Etapa_I', 'Etapa_II', 'Profesional'

    # Relación inversa 1:1
    experiencia = db.relationship("Experiencia", back_populates="practica")

    def __repr__(self):
        return f"<Practica experiencia_id={self.id_experiencia} etapa='{self.etapa}'>"


class Pasantia(db.Model):
    """Subtipo 1:1 de Experiencia para Pasantías."""
    __tablename__ = "pasantias"

    id_experiencia = db.Column(
        db.Integer,
        db.ForeignKey("experiencias.id_experiencia", ondelete="CASCADE"),
        primary_key=True,
    )
    tipo = db.Column(db.String(50), nullable=False)  # ENUM: ej. 'Social', 'Laboral', 'Investigacion'

    # Relación inversa 1:1
    experiencia = db.relationship("Experiencia", back_populates="pasantia")

    def __repr__(self):
        return f"<Pasantia experiencia_id={self.id_experiencia} tipo='{self.tipo}'>"


class AsignacionExperiencia(db.Model):
    """Historial y asignación activa de tutores y supervisores institucionales."""
    __tablename__ = "asignaciones_experiencia"

    id_asignacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_experiencia = db.Column(db.Integer, db.ForeignKey("experiencias.id_experiencia", ondelete="CASCADE"), nullable=False, index=True)
    rol = db.Column(db.String(30), nullable=False)  # ENUM: 'Tutor', 'Supervisor'
    id_tutor = db.Column(db.Integer, db.ForeignKey("tutores_docentes.id_tutor", ondelete="SET NULL"), nullable=True, index=True)
    id_supervisor = db.Column(db.Integer, db.ForeignKey("supervisores_institucionales.id_supervisor", ondelete="SET NULL"), nullable=True, index=True)
    id_entidad = db.Column(db.Integer, db.ForeignKey("entidades_receptoras.id_entidad", ondelete="SET NULL"), nullable=True, index=True)
    fecha_desde = db.Column(db.Date, nullable=False)
    fecha_hasta = db.Column(db.Date, nullable=True)
    activa = db.Column(db.Boolean, default=True, nullable=False)  # UK parcial

    # Relaciones
    experiencia = db.relationship("Experiencia", back_populates="asignaciones")
    tutor = db.relationship("TutorDocente", back_populates="asignaciones")
    supervisor = db.relationship("SupervisorInstitucional", back_populates="asignaciones")
    entidad = db.relationship("EntidadReceptora", back_populates="asignaciones")

    def __repr__(self):
        return f"<AsignacionExperiencia id={self.id_asignacion} exp_id={self.id_experiencia} rol='{self.rol}' activa={self.activa}>"


class PlanTrabajo(db.Model):
    """Versión del plan de trabajo asociado a una experiencia."""
    __tablename__ = "planes_trabajo"
    __table_args__ = (
        db.UniqueConstraint("id_experiencia", "version", name="uq_plan_experiencia_version"),
    )

    id_plan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_experiencia = db.Column(db.Integer, db.ForeignKey("experiencias.id_experiencia", ondelete="CASCADE"), nullable=False, index=True)
    version = db.Column(db.Integer, default=1, nullable=False)  # UK compuesto con id_experiencia
    estado = db.Column(db.String(30), default="Borrador", nullable=False)  # ENUM: 'Borrador', 'Enviado', 'Aprobado', 'Rechazado'
    objetivos = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    fecha_aprobacion = db.Column(db.DateTime, nullable=True)
    aprobado_por_tutor = db.Column(db.Integer, db.ForeignKey("tutores_docentes.id_tutor", ondelete="SET NULL"), nullable=True, index=True)

    # Relaciones
    experiencia = db.relationship("Experiencia", back_populates="planes_trabajo")
    tutor_aprobador = db.relationship("TutorDocente", back_populates="planes_aprobados")
    actividades = db.relationship("ActividadPlan", back_populates="plan", cascade="all, delete-orphan", lazy="select")
    entregables = db.relationship("EntregablePlan", back_populates="plan", cascade="all, delete-orphan", lazy="select")
    hitos = db.relationship("HitoPlan", back_populates="plan", cascade="all, delete-orphan", lazy="select")
    criterios_evaluacion = db.relationship("CriterioEvaluacion", back_populates="plan", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return f"<PlanTrabajo id={self.id_plan} exp_id={self.id_experiencia} v={self.version} estado='{self.estado}'>"


class ActividadPlan(db.Model):
    """Actividad calendarizada dentro del plan de trabajo."""
    __tablename__ = "actividades_plan"

    id_actividad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_plan = db.Column(db.Integer, db.ForeignKey("planes_trabajo.id_plan", ondelete="CASCADE"), nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    horas_estimadas = db.Column(db.Numeric(6, 2), nullable=False, default=0.0)
    estado = db.Column(db.String(30), default="Pendiente", nullable=False)  # ENUM: 'Pendiente', 'En_Progreso', 'Completada', 'Cancelada'

    # Relaciones
    plan = db.relationship("PlanTrabajo", back_populates="actividades")
    entregables = db.relationship("EntregablePlan", back_populates="actividad", lazy="select")

    def __repr__(self):
        return f"<ActividadPlan id={self.id_actividad} plan_id={self.id_plan} estado='{self.estado}'>"


class EntregablePlan(db.Model):
    """Producto o entregable documental/técnico definido en el plan."""
    __tablename__ = "entregables_plan"

    id_entregable = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_plan = db.Column(db.Integer, db.ForeignKey("planes_trabajo.id_plan", ondelete="CASCADE"), nullable=False, index=True)
    id_actividad = db.Column(db.Integer, db.ForeignKey("actividades_plan.id_actividad", ondelete="SET NULL"), nullable=True, index=True)
    nombre = db.Column(db.String(150), nullable=False)
    fecha_entrega_esperada = db.Column(db.Date, nullable=False)
    fecha_entrega_real = db.Column(db.Date, nullable=True)
    estado = db.Column(db.String(30), default="Pendiente", nullable=False)  # ENUM: 'Pendiente', 'Entregado', 'Aprobado', 'Observado'
    ruta_archivo = db.Column(db.String(255), nullable=True)

    # Relaciones
    plan = db.relationship("PlanTrabajo", back_populates="entregables")
    actividad = db.relationship("ActividadPlan", back_populates="entregables")

    def __repr__(self):
        return f"<EntregablePlan id={self.id_entregable} nombre='{self.nombre}' estado='{self.estado}'>"


class HitoPlan(db.Model):
    """Hito o punto de control agendado en el plan de trabajo."""
    __tablename__ = "hitos_plan"

    id_hito = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_plan = db.Column(db.Integer, db.ForeignKey("planes_trabajo.id_plan", ondelete="CASCADE"), nullable=False, index=True)
    descripcion = db.Column(db.String(255), nullable=False)
    fecha_hito = db.Column(db.Date, nullable=False)
    cumplido = db.Column(db.Boolean, default=False, nullable=False)

    # Relaciones
    plan = db.relationship("PlanTrabajo", back_populates="hitos")

    def __repr__(self):
        return f"<HitoPlan id={self.id_hito} fecha='{self.fecha_hito}' cumplido={self.cumplido}>"


class CriterioEvaluacion(db.Model):
    """Criterio de evaluación y porcentaje de ponderación establecido en el plan."""
    __tablename__ = "criterios_evaluacion"

    id_criterio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_plan = db.Column(db.Integer, db.ForeignKey("planes_trabajo.id_plan", ondelete="CASCADE"), nullable=False, index=True)
    descripcion = db.Column(db.String(255), nullable=False)
    peso_porcentaje = db.Column(db.Numeric(5, 2), nullable=False)  # CHECK suma=100

    # Relaciones
    plan = db.relationship("PlanTrabajo", back_populates="criterios_evaluacion")

    def __repr__(self):
        return f"<CriterioEvaluacion id={self.id_criterio} peso={self.peso_porcentaje}%>"


class Evaluacion(db.Model):
    """Calificaciones emitidas por tutores o supervisores institucionales."""
    __tablename__ = "evaluaciones"
    __table_args__ = (
        db.CheckConstraint("calificacion >= 0 AND calificacion <= 100", name="chk_evaluacion_rango"),
    )

    id_evaluacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_experiencia = db.Column(db.Integer, db.ForeignKey("experiencias.id_experiencia", ondelete="CASCADE"), nullable=False, index=True)
    id_tutor = db.Column(db.Integer, db.ForeignKey("tutores_docentes.id_tutor", ondelete="SET NULL"), nullable=True, index=True)
    id_supervisor = db.Column(db.Integer, db.ForeignKey("supervisores_institucionales.id_supervisor", ondelete="SET NULL"), nullable=True, index=True)
    calificacion = db.Column(db.Numeric(5, 2), nullable=False)  # NUMERIC(5,2) 0-100
    comentarios = db.Column(db.Text, nullable=True)
    fecha_evaluacion = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    experiencia = db.relationship("Experiencia", back_populates="evaluaciones")
    tutor = db.relationship("TutorDocente", back_populates="evaluaciones")
    supervisor = db.relationship("SupervisorInstitucional", back_populates="evaluaciones")

    def __repr__(self):
        return f"<Evaluacion id={self.id_evaluacion} exp_id={self.id_experiencia} nota={self.calificacion}>"


class Documento(db.Model):
    """Documentos de respaldo y expedientes vinculados a estudiantes y/o experiencias."""
    __tablename__ = "documentos"

    id_documento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("estudiantes.id_estudiante", ondelete="CASCADE"), nullable=True, index=True)
    id_experiencia = db.Column(db.Integer, db.ForeignKey("experiencias.id_experiencia", ondelete="CASCADE"), nullable=True, index=True)
    tipo_documento = db.Column(db.String(50), nullable=False)  # ej. 'CV', 'Record_Policial', 'Licencia_Conducir', 'Cedula', etc.
    nombre_original = db.Column(db.String(255), nullable=True)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    tamano_bytes = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    fecha_subida = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    estado = db.Column(db.String(30), default="Vigente", nullable=False)  # 'Vigente', 'Pendiente', 'Aprobado', 'Rechazado'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    estudiante = db.relationship("Estudiante", back_populates="documentos")
    experiencia = db.relationship("Experiencia", back_populates="documentos")

    def to_dict(self):
        return {
            "id": self.id_documento,
            "id_documento": self.id_documento,
            "id_estudiante": self.id_estudiante,
            "id_experiencia": self.id_experiencia,
            "tipo_documento": self.tipo_documento,
            "nombre_original": self.nombre_original or (self.ruta_archivo.split("/")[-1] if self.ruta_archivo else "Documento"),
            "ruta_archivo": self.ruta_archivo,
            "tamano_bytes": self.tamano_bytes or 0,
            "mime_type": self.mime_type or "application/octet-stream",
            "fecha_subida": self.fecha_subida.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_subida else "",
            "estado": self.estado,
        }

    def __repr__(self):
        return f"<Documento id={self.id_documento} tipo='{self.tipo_documento}' archivo='{self.nombre_original}'>"
