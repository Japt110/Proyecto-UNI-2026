"""Únicamente se registra el modelo vigente; las tablas anteriores no se recrean."""
from database import db
from models.schema import TABLES
from models.base import Estudiante, Usuario
from models.auth import AuthSession

__all__ = ["db", "TABLES", "Estudiante", "Usuario", "AuthSession"]
