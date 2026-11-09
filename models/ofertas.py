"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - OFERTAS Y POSTULACIONES
===============================================================================
Modelos ORM relacionales para la publicación de convocatorias y postulaciones:
- OfertaPasantia (ofertas_pasantia): Convocatorias públicas de pasantías
- AplicacionOferta (aplicaciones_oferta): Solicitudes/postulaciones de estudiantes
===============================================================================
"""

from datetime import datetime, timezone
from database import db


class OfertaPasantia(db.Model):
    """Convocatoria u oferta de pasantía publicada para la comunidad estudiantil."""
    __tablename__ = "ofertas_pasantia"

    id_oferta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(150), nullable=False, index=True)
    tipo = db.Column(db.String(50), nullable=False, default="Académica")      # 'Académica', 'Profesional'
    modalidad = db.Column(db.String(30), nullable=False, default="Presencial") # 'Presencial', 'Virtual', 'Híbrida'
    duracion = db.Column(db.String(30), nullable=False, default="160H")        # Etiqueta visual (ej. '160H', '240H')
    duracion_horas = db.Column(db.Integer, nullable=False, default=160)
    experiencia = db.Column(db.String(50), nullable=False, default="Sin experiencia") # 'Sin experiencia', 'Prácticas', 'Junior'
    sector = db.Column(db.String(50), nullable=False, default="Tecnología")    # 'Tecnología', 'Química', 'Industrial', 'Civil', 'Eléctrica'
    ciudad = db.Column(db.String(100), nullable=False, default="Managua")
    descripcion = db.Column(db.Text, nullable=False)
    requisitos = db.Column(db.Text, nullable=True)
    condiciones = db.Column(db.String(100), nullable=True, default="No remunerada")  # ej. 'Remunerada', 'Estipendio de transporte', 'Horario flexible'
    cupos = db.Column(db.Integer, nullable=False, default=1)
    estado = db.Column(db.String(30), nullable=False, default="Activo")        # 'Activo', 'Cerrado', 'En_Revision'

    # Claves foráneas opcionales para integración con entidades del sistema
    id_entidad = db.Column(db.Integer, db.ForeignKey("entidades_receptoras.id_entidad", ondelete="SET NULL"), nullable=True, index=True)
    id_municipio = db.Column(db.Integer, db.ForeignKey("municipios.id_municipio", ondelete="SET NULL"), nullable=True, index=True)
    id_carrera = db.Column(db.Integer, db.ForeignKey("carreras.id_carrera", ondelete="SET NULL"), nullable=True, index=True)
    id_usuario_creador = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), nullable=True, index=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    entidad = db.relationship("EntidadReceptora", lazy="select")
    municipio = db.relationship("Municipio", lazy="select")
    carrera = db.relationship("Carrera", lazy="select")
    creador = db.relationship("Usuario", lazy="select")
    aplicaciones = db.relationship("AplicacionOferta", back_populates="oferta", cascade="all, delete-orphan", lazy="select")

    def to_dict(self):
        """Serializa la oferta para su consumo por el frontend."""
        return {
            "id": self.id_oferta,
            "titulo": self.titulo,
            "tipo": self.tipo,
            "modalidad": self.modalidad,
            "duracion": self.duracion,
            "duracion_horas": self.duracion_horas,
            "experiencia": self.experiencia,
            "sector": self.sector,
            "ciudad": self.ciudad,
            "descripcion": self.descripcion,
            "requisitos": self.requisitos,
            "condiciones": self.condiciones or "No remunerada",
            "cupos": self.cupos,
            "estado": self.estado,
            "entidad_nombre": self.entidad.nombre if self.entidad else None,
            "id_entidad": self.id_entidad,
            "carrera_nombre": self.carrera.nombre if self.carrera else None,
            "total_postulantes": len(self.aplicaciones) if self.aplicaciones else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<OfertaPasantia id={self.id_oferta} titulo='{self.titulo}' sector='{self.sector}' estado='{self.estado}'>"


class AplicacionOferta(db.Model):
    """Solicitud o postulación de un estudiante a una oferta de pasantía."""
    __tablename__ = "aplicaciones_oferta"
    __table_args__ = (
        db.UniqueConstraint("id_oferta", "id_estudiante", name="uq_oferta_estudiante_aplicacion"),
    )

    id_aplicacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_oferta = db.Column(db.Integer, db.ForeignKey("ofertas_pasantia.id_oferta", ondelete="CASCADE"), nullable=False, index=True)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("estudiantes.id_estudiante", ondelete="CASCADE"), nullable=False, index=True)
    fecha_postulacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    estado = db.Column(db.String(30), default="Pendiente", nullable=False)  # 'Pendiente', 'Aceptada', 'Rechazada', 'Cancelada'
    mensaje = db.Column(db.Text, nullable=True)
    id_experiencia_generada = db.Column(db.Integer, db.ForeignKey("experiencias.id_experiencia", ondelete="SET NULL"), nullable=True, index=True)
    documentos_compartidos = db.Column(db.Text, nullable=True)  # JSON array de IDs de documentos compartidos para esta postulación

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones
    oferta = db.relationship("OfertaPasantia", back_populates="aplicaciones")
    estudiante = db.relationship("Estudiante", lazy="select")
    experiencia_generada = db.relationship("Experiencia", lazy="select")

    def to_dict(self):
        return {
            "id_aplicacion": self.id_aplicacion,
            "id_oferta": self.id_oferta,
            "oferta_titulo": self.oferta.titulo if self.oferta else None,
            "id_estudiante": self.id_estudiante,
            "estudiante_nombre": f"{self.estudiante.nombre} {self.estudiante.apellido}" if self.estudiante else None,
            "estudiante_cup": self.estudiante.cup if self.estudiante else None,
            "fecha_postulacion": self.fecha_postulacion.isoformat() if self.fecha_postulacion else None,
            "estado": self.estado,
            "mensaje": self.mensaje,
            "id_experiencia_generada": self.id_experiencia_generada,
            "documentos_compartidos": self.documentos_compartidos,
        }

    def __repr__(self):
        return f"<AplicacionOferta id={self.id_aplicacion} oferta_id={self.id_oferta} estudiante_id={self.id_estudiante} estado='{self.estado}'>"
