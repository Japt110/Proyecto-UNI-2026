"""Catálogos del modelo socioacadémico."""
from database import db
from models.schema import TABLES

class Pais(db.Model):
    __table__ = TABLES["paises"]
class Etnia(db.Model):
    __table__ = TABLES["etnias"]
class Departamento(db.Model):
    __table__ = TABLES["departamentos"]
class Municipio(db.Model):
    __table__ = TABLES["municipios"]
class CentroEducativo(db.Model):
    __table__ = TABLES["centros_educativos"]
class AreaCarrera(db.Model):
    __table__ = TABLES["areas_carrera"]
class Carrera(db.Model):
    __table__ = TABLES["carreras"]
class Beca(db.Model):
    __table__ = TABLES["becas"]
