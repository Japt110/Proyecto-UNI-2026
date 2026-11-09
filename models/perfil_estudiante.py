"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - SUBDOMINIO B: PERFIL SOCIO-ACADÉMICO
===============================================================================
Modelos ORM relacionales para la ficha socio-académica del estudiante:
- Estudiante (estudiantes): Datos demográficos, de origen y ficha personal
- DireccionEstudiante (direcciones_estudiante): Direcciones de residencia
- TelefonoEstudiante (telefonos_estudiante): Números de contacto
- EducacionPreviaEstudiante (educacion_previa_estudiante): Antecedentes educativos
- Matricula (matriculas): Historial de matrícula académica y becas
===============================================================================
"""

from datetime import datetime, timezone, date
from database import db


class Estudiante(db.Model):
    """Ficha principal del estudiante."""
    __tablename__ = "estudiantes"

    id_estudiante = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cup = db.Column(db.String(30), nullable=False, unique=True, index=True)      # Código Único Permanente
    cedula = db.Column(db.String(20), nullable=False, unique=True, index=True)   # Cédula de identidad
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    edad = db.Column(db.Integer, nullable=True)  # GENERATED STORED / calculado
    sexo = db.Column(db.String(20), nullable=False)  # ENUM: 'Masculino', 'Femenino', etc.
    dimension_nacional = db.Column(db.String(50), nullable=True)  # ENUM
    id_pais_origen = db.Column(db.Integer, db.ForeignKey("paises.id_pais", ondelete="RESTRICT"), nullable=False, index=True)
    id_etnia = db.Column(db.Integer, db.ForeignKey("etnias.id_etnia", ondelete="RESTRICT"), nullable=False, index=True)
    estado_civil = db.Column(db.String(30), nullable=True)  # ENUM
    hijos = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones Catálogos
    pais_origen = db.relationship("Pais", back_populates="estudiantes")
    etnia = db.relationship("Etnia", back_populates="estudiantes")

    # Relaciones Perfil
    direcciones = db.relationship("DireccionEstudiante", back_populates="estudiante", cascade="all, delete-orphan", lazy="select")
    telefonos = db.relationship("TelefonoEstudiante", back_populates="estudiante", cascade="all, delete-orphan", lazy="select")
    educaciones_previas = db.relationship("EducacionPreviaEstudiante", back_populates="estudiante", cascade="all, delete-orphan", lazy="select")
    matriculas = db.relationship("Matricula", back_populates="estudiante", cascade="all, delete-orphan", lazy="select")

    # Relaciones Experiencias & Usuario & Documentos
    experiencias = db.relationship("Experiencia", back_populates="estudiante", cascade="all, delete-orphan", lazy="select")
    documentos = db.relationship("Documento", back_populates="estudiante", cascade="all, delete-orphan", lazy="select")
    usuario = db.relationship("Usuario", back_populates="estudiante", uselist=False, lazy="select")

    def calcular_edad(self) -> int:
        """Calcula la edad a partir de la fecha de nacimiento."""
        if not self.fecha_nacimiento:
            return 0
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad

    def __repr__(self):
        return f"<Estudiante id={self.id_estudiante} cup='{self.cup}' cedula='{self.cedula}' nombre='{self.nombre} {self.apellido}'>"


class DireccionEstudiante(db.Model):
    """Dirección domiciliar de residencia del estudiante."""
    __tablename__ = "direcciones_estudiante"

    id_direccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("estudiantes.id_estudiante", ondelete="CASCADE"), nullable=False, index=True)
    id_municipio = db.Column(db.Integer, db.ForeignKey("municipios.id_municipio", ondelete="RESTRICT"), nullable=False, index=True)
    comunidad = db.Column(db.String(100), nullable=True)
    direccion_domiciliar = db.Column(db.Text, nullable=False)
    zona = db.Column(db.String(20), nullable=False)  # ENUM: 'Urbano', 'Rural'
    es_principal = db.Column(db.Boolean, default=False, nullable=False)  # UK parcial

    # Relaciones
    estudiante = db.relationship("Estudiante", back_populates="direcciones")
    municipio = db.relationship("Municipio", back_populates="direcciones")

    def __repr__(self):
        return f"<DireccionEstudiante id={self.id_direccion} estudiante_id={self.id_estudiante} zona='{self.zona}'>"


class TelefonoEstudiante(db.Model):
    """Teléfono de contacto del estudiante."""
    __tablename__ = "telefonos_estudiante"

    id_telefono = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("estudiantes.id_estudiante", ondelete="CASCADE"), nullable=False, index=True)
    numero = db.Column(db.String(30), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)  # ENUM: ej. 'Móvil', 'Fijo', 'WhatsApp', 'Tutor'
    es_principal = db.Column(db.Boolean, default=False, nullable=False)  # UK parcial

    # Relaciones
    estudiante = db.relationship("Estudiante", back_populates="telefonos")

    def __repr__(self):
        return f"<TelefonoEstudiante id={self.id_telefono} numero='{self.numero}' tipo='{self.tipo}'>"


class EducacionPreviaEstudiante(db.Model):
    """Historial de educación secundaria o técnica previa del estudiante."""
    __tablename__ = "educacion_previa_estudiante"

    id_educacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("estudiantes.id_estudiante", ondelete="CASCADE"), nullable=False, index=True)
    id_centro_educativo = db.Column(db.Integer, db.ForeignKey("centros_educativos.id_centro", ondelete="RESTRICT"), nullable=False, index=True)
    educacion_tecnica = db.Column(db.String(150), nullable=True)
    titulo_obtenido = db.Column(db.String(150), nullable=False)
    anio_graduacion = db.Column(db.Integer, nullable=False)

    # Relaciones
    estudiante = db.relationship("Estudiante", back_populates="educaciones_previas")
    centro_educativo = db.relationship("CentroEducativo", back_populates="educaciones_previas")

    def __repr__(self):
        return f"<EducacionPrevia id={self.id_educacion} titulo='{self.titulo_obtenido}' anio={self.anio_graduacion}'>"


class Matricula(db.Model):
    """Registro de matrícula académica del estudiante."""
    __tablename__ = "matriculas"

    id_matricula = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_estudiante = db.Column(db.Integer, db.ForeignKey("estudiantes.id_estudiante", ondelete="CASCADE"), nullable=False, index=True)
    id_carrera = db.Column(db.Integer, db.ForeignKey("carreras.id_carrera", ondelete="RESTRICT"), nullable=False, index=True)
    periodo_academico = db.Column(db.String(30), nullable=False)  # ej. "I Semestre 2026"
    anio_academico = db.Column(db.Integer, nullable=False)       # ej. 1, 2, 3, 4, 5
    modalidad = db.Column(db.String(50), nullable=False)        # ENUM: ej. 'Regular', 'Por Encuentros', 'Virtual'
    turno = db.Column(db.String(30), nullable=False)            # ENUM: ej. 'Matutino', 'Vespertino', 'Nocturno', 'Sabatino'
    grupo_clase = db.Column(db.String(30), nullable=True)       # ej. '4M1-CO'
    id_beca = db.Column(db.Integer, db.ForeignKey("becas.id_beca", ondelete="SET NULL"), nullable=True, index=True)
    estado = db.Column(db.String(30), nullable=False, default="Activa")  # ENUM: 'Activa', 'Retirada', 'Finalizada'

    # Relaciones
    estudiante = db.relationship("Estudiante", back_populates="matriculas")
    carrera = db.relationship("Carrera", back_populates="matriculas")
    beca = db.relationship("Beca", back_populates="matriculas")

    def __repr__(self):
        return f"<Matricula id={self.id_matricula} estudiante_id={self.id_estudiante} carrera_id={self.id_carrera} estado='{self.estado}'>"
