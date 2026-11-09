"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - BASE & COMPATIBILIDAD
===============================================================================
Redirección de entidades principales al nuevo modelo relacional:
- Usuario -> models.usuarios_auditoria.Usuario
- Estudiante -> models.perfil_estudiante.Estudiante
===============================================================================
"""

from models.usuarios_auditoria import Usuario
from models.perfil_estudiante import Estudiante


class Persona:
    """Clase de compatibilidad no mapeada al ORM."""
    query = None


class Trabajador:
    """Clase de compatibilidad no mapeada al ORM."""
    query = None


__all__ = ["Usuario", "Estudiante", "Persona", "Trabajador"]