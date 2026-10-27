"""
===============================================================================
EVENTOS-UNI - MODELOS DE ENTIDADES BASE Y PADRÓN UNIVERSITARIO (5FN)
===============================================================================
Define la jerarquía de herencia relacional 1:1 para el padrón universitario:
- Persona: Supertipo base que contiene los datos de identidad ciudadana/universitaria.
- Estudiante: Subtipo de Persona que almacena información académica y grupo.
- Trabajador: Subtipo de Persona que almacena datos laborales y cargo.
- Usuario: Cuenta de acceso al sistema con autenticación y asignación de rol (RBAC).
===============================================================================
"""

import uuid
from database import db
from core.security import hash_password, verify_password


# -----------------------------------------------------------------------------
# 1. Supertipo Base: Persona (Padrón Universitario Unificado)
# -----------------------------------------------------------------------------

class Persona(db.Model):
    """
    Modelo ORM supertipo que representa a un miembro de la comunidad universitaria
    (Estudiante, Docente o Administrativo) registrado en el padrón.
    """
    __tablename__ = "personas"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero_unico = db.Column(db.String(30), nullable=False, unique=True, index=True)  # Código único NUP
    cedula = db.Column(db.String(30), nullable=False, unique=True, index=True)        # Cédula de identidad
    nombres_apellidos = db.Column(db.String(150), nullable=False)
    sexo = db.Column(db.String(20), nullable=False)
    ciudad_residencia_id = db.Column(db.String(36), db.ForeignKey("ciudades.id"), nullable=False)
    ciudad_procedencia_id = db.Column(db.String(36), db.ForeignKey("ciudades.id"), nullable=False)
    sede_id = db.Column(db.String(36), db.ForeignKey("sedes.id"), nullable=False)

    # Relaciones relacionales
    ciudad_residencia = db.relationship("Ciudad", foreign_keys=[ciudad_residencia_id], backref="personas_residentes")
    ciudad_procedencia = db.relationship("Ciudad", foreign_keys=[ciudad_procedencia_id], backref="personas_procedentes")

    # Polimorfismo 1:1
    estudiante = db.relationship("Estudiante", backref="persona", uselist=False, cascade="all, delete-orphan")
    trabajador = db.relationship("Trabajador", backref="persona", uselist=False, cascade="all, delete-orphan")
    asistencias = db.relationship("Asistencia", backref="persona")


# -----------------------------------------------------------------------------
# 2. Subtipo: Estudiante (Relación 1:1 estricta con Persona)
# -----------------------------------------------------------------------------

class Estudiante(db.Model):
    """Modelo ORM subtipo que contiene la ficha académica de un estudiante."""
    __tablename__ = "estudiantes"

    # persona_id actúa como Clave Primaria y Foránea simultáneamente (Patrón Subtipo 1:1)
    persona_id = db.Column(db.String(36), db.ForeignKey("personas.id", ondelete="CASCADE"), primary_key=True)
    carnet_estudiante = db.Column(db.String(30), nullable=False, unique=True, index=True)
    area_conocimiento_id = db.Column(db.String(36), db.ForeignKey("unidades_organizativas.id"), nullable=False)
    carrera = db.Column(db.String(100), nullable=False)
    ano_academico = db.Column(db.String(30), nullable=False)
    grupo = db.Column(db.String(20), nullable=False)  # Útil para justificación automática de inasistencias
    turno = db.Column(db.String(30), nullable=False)


# -----------------------------------------------------------------------------
# 3. Subtipo: Trabajador / Docente (Relación 1:1 estricta con Persona)
# -----------------------------------------------------------------------------

class Trabajador(db.Model):
    """Modelo ORM subtipo que almacena los datos laborales de docentes y administrativos."""
    __tablename__ = "trabajadores"

    # persona_id actúa como Clave Primaria y Foránea simultáneamente (Patrón Subtipo 1:1)
    persona_id = db.Column(db.String(36), db.ForeignKey("personas.id", ondelete="CASCADE"), primary_key=True)
    codigo_trabajador = db.Column(db.String(30), nullable=False, unique=True, index=True)
    unidad_id = db.Column(db.String(36), db.ForeignKey("unidades_organizativas.id"), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    condicion_laboral = db.Column(db.String(50), nullable=False)  # ej. "Planta", "Horas Clase"


# -----------------------------------------------------------------------------
# 4. Entidad de Autenticación: Usuario del Sistema
# -----------------------------------------------------------------------------

class Usuario(db.Model):
    """Modelo ORM que gestiona las credenciales y el rol (RBAC) de acceso a la plataforma."""
    __tablename__ = "usuarios"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    unidad_id = db.Column(db.String(36), db.ForeignKey("unidades_organizativas.id"), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), nullable=False)  # ej. "Rector", "Encargado", "Asistencia"

    def set_password(self, password: str):
        """Asigna el hash seguro PBKDF2:SHA256 a la contraseña del usuario."""
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña ingresada coincide con el hash guardado."""
        return verify_password(self.password_hash, password)