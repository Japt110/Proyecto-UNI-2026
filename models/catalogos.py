"""
===============================================================================
EVENTOS-UNI - MODELOS DE CATÁLOGOS INSTITUCIONALES, GEOGRÁFICOS Y ESTRATÉGICOS
===============================================================================
Define los modelos ORM relacionales para las entidades de catálogo base:
- Departamento: División político-administrativa
- Ciudad: Municipio o ciudad pertenecientes a un departamento
- Sede: Recintos universitarios (RUSB, RUPAP, Sede Norte, etc.)
- EspacioFisico: Auditorios, laboratorios, plazoletas y recintos
- UnidadOrganizativa: Facultades, direcciones y dependencias organizativas
- TipoActividad: Categorización formal de los eventos universitarios con descripción
- EjeLineamiento, Lineamiento, AccionEstrategica: Estrategia Nacional de Educación 2026
===============================================================================
"""

import uuid
from database import db


# -----------------------------------------------------------------------------
# 1. Catálogos Geográficos (Departamentos y Ciudades)
# -----------------------------------------------------------------------------

class Departamento(db.Model):
    """Modelo ORM que representa un departamento del país."""
    __tablename__ = "departamentos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    # Relaciones
    ciudades = db.relationship("Ciudad", backref="departamento", cascade="all, delete-orphan")


class Ciudad(db.Model):
    """Modelo ORM que representa un municipio o ciudad dentro de un departamento."""
    __tablename__ = "ciudades"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(100), nullable=False)
    departamento_id = db.Column(db.String(36), db.ForeignKey("departamentos.id", ondelete="CASCADE"), nullable=False)

    # Relaciones
    sedes = db.relationship("Sede", backref="ciudad")


# -----------------------------------------------------------------------------
# 2. Catálogo de Sedes / Recintos Universitarios
# -----------------------------------------------------------------------------

class Sede(db.Model):
    """Modelo ORM que representa un recinto o sede física de la universidad."""
    __tablename__ = "sedes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), nullable=False, unique=True, index=True)
    ciudad_id = db.Column(db.String(36), db.ForeignKey("ciudades.id"), nullable=False)

    # Relaciones relacionales
    espacios = db.relationship("EspacioFisico", backref="sede", cascade="all, delete-orphan")
    personas = db.relationship("Persona", backref="sede")


# -----------------------------------------------------------------------------
# 3. Catálogo de Espacios Físicos (Locaciones internas)
# -----------------------------------------------------------------------------

class EspacioFisico(db.Model):
    """Modelo ORM que representa auditorios, laboratorios o salas dentro de una sede."""
    __tablename__ = "espacios_fisicos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sede_id = db.Column(db.String(36), db.ForeignKey("sedes.id", ondelete="CASCADE"), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False, default=0)

    # Relaciones relacionales
    actividades = db.relationship("Actividad", backref="espacio_fisico")


# -----------------------------------------------------------------------------
# 4. Catálogo de Unidades Organizativas (Facultades / Direcciones)
# -----------------------------------------------------------------------------

class UnidadOrganizativa(db.Model):
    """Modelo ORM que representa facultades, direcciones o decanatos organizadores."""
    __tablename__ = "unidades_organizativas"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(120), nullable=False)
    codigo = db.Column(db.String(20), nullable=False, unique=True, index=True)
    nivel_jerarquico = db.Column(db.String(50), nullable=False)  # ej. "Dirección", "Facultad"

    # Relaciones relacionales
    usuarios = db.relationship("Usuario", backref="unidad")
    estudiantes = db.relationship("Estudiante", backref="area_conocimiento")
    trabajadores = db.relationship("Trabajador", backref="unidad")
    actividades_organizadas = db.relationship("Actividad", backref="unidad_responsable")


# -----------------------------------------------------------------------------
# 5. Catálogo de Tipos de Actividad
# -----------------------------------------------------------------------------

class TipoActividad(db.Model):
    """Modelo ORM que categoriza las actividades (Feria, Conferencia, Taller, Simposio)."""
    __tablename__ = "tipos_actividad"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=True)

    # Relaciones relacionales
    actividades = db.relationship("Actividad", backref="tipo")


# -----------------------------------------------------------------------------
# 6. Módulo Estrategia Nacional de Educación 2026 (Ejes, Lineamientos y Acciones)
# -----------------------------------------------------------------------------

class EjeLineamiento(db.Model):
    """Modelo ORM que representa un Eje Estratégico de la Estrategia Nacional de Educación."""
    __tablename__ = "ejes_lineamiento"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_oficial = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

    # Relaciones
    lineamientos = db.relationship("Lineamiento", backref="eje", cascade="all, delete-orphan")


class Lineamiento(db.Model):
    """Modelo ORM que representa un Lineamiento específico dentro de un Eje Estratégico."""
    __tablename__ = "lineamientos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    eje_id = db.Column(db.String(36), db.ForeignKey("ejes_lineamiento.id", ondelete="CASCADE"), nullable=False)
    numero_oficial = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

    # Relaciones
    acciones = db.relationship("AccionEstrategica", backref="lineamiento", cascade="all, delete-orphan")


class AccionEstrategica(db.Model):
    """Modelo ORM que representa una Acción Estratégica derivada de un Lineamiento."""
    __tablename__ = "acciones_estrategicas"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lineamiento_id = db.Column(db.String(36), db.ForeignKey("lineamientos.id", ondelete="CASCADE"), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)