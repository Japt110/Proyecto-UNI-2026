"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - SUBDOMINIO A: CATÁLOGOS
===============================================================================
Modelos ORM relacionales para entidades de catálogo base:
- Pais (paises): Procedencia geográfica internacional
- Etnia (etnias): Autoidentificación cultural / étnica
- Departamento (departamentos): División político-administrativa
- Municipio (municipios): División territorial dependiente de departamento
- CentroEducativo (centros_educativos): Colegios / institutos de procedencia
- AreaCarrera (areas_carrera): Agrupación académica de carreras
- Carrera (carreras): Programas de formación universitaria
- Beca (becas): Beneficios de beca otorgados en matrículas
===============================================================================
"""

from database import db


class Pais(db.Model):
    """Catálogo de países para la procedencia de estudiantes."""
    __tablename__ = "paises"

    id_pais = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    codigo_iso = db.Column(db.String(3), nullable=False, unique=True, index=True)

    # Relaciones
    estudiantes = db.relationship("Estudiante", back_populates="pais_origen", lazy="select")

    def __repr__(self):
        return f"<Pais id={self.id_pais} nombre='{self.nombre}' codigo_iso='{self.codigo_iso}'>"


class Etnia(db.Model):
    """Catálogo de autoidentificación étnica."""
    __tablename__ = "etnias"

    id_etnia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)

    # Relaciones
    estudiantes = db.relationship("Estudiante", back_populates="etnia", lazy="select")

    def __repr__(self):
        return f"<Etnia id={self.id_etnia} nombre='{self.nombre}'>"


class Departamento(db.Model):
    """Catálogo de departamentos geográficos."""
    __tablename__ = "departamentos"

    id_departamento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)

    # Relaciones
    municipios = db.relationship("Municipio", back_populates="departamento", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return f"<Departamento id={self.id_departamento} nombre='{self.nombre}'>"


class Municipio(db.Model):
    """Catálogo de municipios pertenecientes a un departamento."""
    __tablename__ = "municipios"

    id_municipio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_departamento = db.Column(db.Integer, db.ForeignKey("departamentos.id_departamento", ondelete="CASCADE"), nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)

    # Relaciones
    departamento = db.relationship("Departamento", back_populates="municipios")
    direcciones = db.relationship("DireccionEstudiante", back_populates="municipio", lazy="select")
    centros_educativos = db.relationship("CentroEducativo", back_populates="municipio", lazy="select")

    def __repr__(self):
        return f"<Municipio id={self.id_municipio} nombre='{self.nombre}'>"


class CentroEducativo(db.Model):
    """Catálogo de colegios o centros de procedencia estudiantil."""
    __tablename__ = "centros_educativos"

    id_centro = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # ENUM: 'Privado', 'Estatal'
    id_municipio = db.Column(db.Integer, db.ForeignKey("municipios.id_municipio", ondelete="RESTRICT"), nullable=False, index=True)

    # Relaciones
    municipio = db.relationship("Municipio", back_populates="centros_educativos")
    educaciones_previas = db.relationship("EducacionPreviaEstudiante", back_populates="centro_educativo", lazy="select")

    def __repr__(self):
        return f"<CentroEducativo id={self.id_centro} nombre='{self.nombre}' tipo='{self.tipo}'>"


class AreaCarrera(db.Model):
    """Áreas de conocimiento que agrupan a las carreras."""
    __tablename__ = "areas_carrera"

    id_area = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)

    # Relaciones
    carreras = db.relationship("Carrera", back_populates="area", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return f"<AreaCarrera id={self.id_area} nombre='{self.nombre}'>"


class Carrera(db.Model):
    """Catálogo de carreras universitarias."""
    __tablename__ = "carreras"

    id_carrera = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    id_area = db.Column(db.Integer, db.ForeignKey("areas_carrera.id_area", ondelete="RESTRICT"), nullable=False, index=True)
    duracion_anios = db.Column(db.Integer, nullable=False, default=5)

    # Relaciones
    area = db.relationship("AreaCarrera", back_populates="carreras")
    matriculas = db.relationship("Matricula", back_populates="carrera", lazy="select")

    def __repr__(self):
        return f"<Carrera id={self.id_carrera} nombre='{self.nombre}'>"


class Beca(db.Model):
    """Catálogo de becas que se pueden otorgar en las matrículas."""
    __tablename__ = "becas"

    id_beca = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    tipo = db.Column(db.String(50), nullable=False)  # ENUM: ej. 'Completa', 'Parcial', 'Alimenticia', 'Exoneración'

    # Relaciones
    matriculas = db.relationship("Matricula", back_populates="beca", lazy="select")

    def __repr__(self):
        return f"<Beca id={self.id_beca} nombre='{self.nombre}' tipo='{self.tipo}'>"


# -----------------------------------------------------------------------------
# Stubs de compatibilidad hacia atrás (NO mapeados en SQLAlchemy)
# -----------------------------------------------------------------------------
class Sede:
    query = None

class Ciudad:
    query = None

class EspacioFisico:
    query = None

class UnidadOrganizativa:
    query = None

class TipoActividad:
    query = None

class EjeLineamiento:
    query = None

class Lineamiento:
    query = None

class AccionEstrategica:
    query = None