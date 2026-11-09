"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - SUBDOMINIO C: ACTORES EXTERNOS
===============================================================================
Modelos ORM relacionales para entidades receptoras, tutores y supervisores:
- EntidadReceptora (entidades_receptoras): Empresas o instituciones anfitrionas
- TutorDocente (tutores_docentes): Docentes asignados como tutores académicos
- SupervisorInstitucional (supervisores_institucionales): Responsables en la empresa
===============================================================================
"""

from datetime import datetime, timezone
from database import db


class EntidadReceptora(db.Model):
    """Empresas, instituciones u organizaciones receptoras de practicantes/pasantes."""
    __tablename__ = "entidades_receptoras"

    id_entidad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(150), nullable=False, index=True)
    tipo = db.Column(db.String(50), nullable=False)  # ENUM: ej. 'Privada', 'Pública', 'ONG', 'Mixta'
    contacto_nombre = db.Column(db.String(100), nullable=True)
    contacto_email = db.Column(db.String(120), nullable=True)
    contacto_telefono = db.Column(db.String(30), nullable=True)
    estado_aprobacion = db.Column(db.String(30), default="Aprobada", nullable=True)  # 'Pendiente_Aprobacion', 'Aprobada', 'Rechazada'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    supervisores = db.relationship("SupervisorInstitucional", back_populates="entidad", cascade="all, delete-orphan", lazy="select")
    asignaciones = db.relationship("AsignacionExperiencia", back_populates="entidad", lazy="select")

    def to_dict(self):
        return {
            "id_entidad": self.id_entidad,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "contacto_nombre": self.contacto_nombre,
            "contacto_email": self.contacto_email,
            "contacto_telefono": self.contacto_telefono,
            "estado_aprobacion": self.estado_aprobacion or "Aprobada",
            "supervisores": [f"{s.nombre} {s.apellido} ({s.cargo})" for s in self.supervisores] if self.supervisores else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<EntidadReceptora id={self.id_entidad} nombre='{self.nombre}' estado='{self.estado_aprobacion}'>"


class TutorDocente(db.Model):
    """Docente de la universidad asignado para tutoría y seguimiento."""
    __tablename__ = "tutores_docentes"

    id_tutor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    departamento = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    asignaciones = db.relationship("AsignacionExperiencia", back_populates="tutor", lazy="select")
    evaluaciones = db.relationship("Evaluacion", back_populates="tutor", lazy="select")
    planes_aprobados = db.relationship("PlanTrabajo", back_populates="tutor_aprobador", lazy="select")
    usuario = db.relationship("Usuario", back_populates="tutor", uselist=False, lazy="select")

    def __repr__(self):
        return f"<TutorDocente id={self.id_tutor} nombre='{self.nombre} {self.apellido}'>"


class SupervisorInstitucional(db.Model):
    """Supervisor de campo asignado por la entidad receptora."""
    __tablename__ = "supervisores_institucionales"

    id_supervisor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=True)
    id_entidad = db.Column(db.Integer, db.ForeignKey("entidades_receptoras.id_entidad", ondelete="RESTRICT"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    entidad = db.relationship("EntidadReceptora", back_populates="supervisores")
    asignaciones = db.relationship("AsignacionExperiencia", back_populates="supervisor", lazy="select")
    evaluaciones = db.relationship("Evaluacion", back_populates="supervisor", lazy="select")
    usuario = db.relationship("Usuario", back_populates="supervisor", uselist=False, lazy="select")

    def __repr__(self):
        return f"<SupervisorInstitucional id={self.id_supervisor} nombre='{self.nombre} {self.apellido}' cargo='{self.cargo}'>"
