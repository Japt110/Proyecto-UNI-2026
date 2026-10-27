"""
===============================================================================
EVENTOS-UNI - MÓDULO CORE (SEGURIDAD Y VALIDACIÓN)
===============================================================================
Expora utilidades centralizadas de hashing, decoradores de autenticación RBAC
y funciones de validación/sanitización de entradas.
===============================================================================
"""

from core.security import (
    hash_password,
    verify_password,
    login_required,
    roles_required
)
from core.validators import (
    validate_email,
    validate_identifier,
    validate_iso_date,
    validate_iso_time,
    sanitize_string
)

__all__ = [
    "hash_password",
    "verify_password",
    "login_required",
    "roles_required",
    "validate_email",
    "validate_identifier",
    "validate_iso_date",
    "validate_iso_time",
    "sanitize_string",
]