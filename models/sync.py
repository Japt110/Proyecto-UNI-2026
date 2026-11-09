"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - SYNC (LEGADO / STUBS)
===============================================================================
Stubs de compatibilidad para evitar errores de importación en módulos heredados.
No registra tablas en el ORM de SQLAlchemy.
===============================================================================
"""


class NodoCliente:
    query = None


class LoteSincronizacion:
    query = None


class ConflictoSincronizacion:
    query = None


class BitacoraAccion:
    query = None


class Tombstone:
    query = None


class RegistroConsulta:
    query = None

    def __init__(self, *args, **kwargs):
        pass


__all__ = [
    "NodoCliente",
    "LoteSincronizacion",
    "ConflictoSincronizacion",
    "BitacoraAccion",
    "Tombstone",
    "RegistroConsulta",
]
