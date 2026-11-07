"""Entidades de identidad y acceso del modelo socioacadémico."""
from datetime import date
from sqlalchemy.orm import synonym
from database import db
from models.schema import estudiantes, usuarios
from core.security import hash_password, verify_password


class Estudiante(db.Model):
    __table__ = estudiantes

    @property
    def nombre_completo(self):
        return " ".join(filter(None, (self.nombre, self.apellido)))

    @property
    def edad_actual(self):
        if self.fecha_nacimiento is None:
            return None
        today = date.today()
        born = self.fecha_nacimiento
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class Usuario(db.Model):
    __table__ = usuarios
    id = synonym("id_usuario")
    estudiante = db.relationship("Estudiante", foreign_keys=[usuarios.c.id_estudiante])

    @property
    def nombre_visible(self):
        return self.estudiante.nombre_completo if self.estudiante else self.nombre_usuario

    def set_password(self, password):
        self.password_hash = hash_password(password)

    def check_password(self, password):
        return verify_password(self.password_hash, password)
