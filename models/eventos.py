"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - EVENTOS (LEGADO / STUBS)
===============================================================================
Stubs de compatibilidad para evitar errores de importación en rutas heredadas.
No registra tablas en el ORM de SQLAlchemy.
===============================================================================
"""


class Actividad:
    query = None


class ActividadLineamiento:
    query = None


class Asistencia:
    query = None


__all__ = ["Actividad", "ActividadLineamiento", "Asistencia"]