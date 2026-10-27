"""
===============================================================================
EVENTOS-UNI - MÓDULO DE VALIDACIÓN Y SANITIZACIÓN DE ENTRADAS (`core/validators.py`)
===============================================================================
Proporciona utilidades para la validación estricta de formatos (Email, ISO Dates,
Identificadores Universitarios) y sanitización contra inyecciones e insumos maliciosos.
===============================================================================
"""

import re
from datetime import datetime
from typing import Tuple, Optional


LETTERS_NICA = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

# -----------------------------------------------------------------------------
# Expresiones Regulares de Validación
# -----------------------------------------------------------------------------
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
CEDULA_REGEX = re.compile(r"^\d{3}-\d{6}-\d{4}[A-Z]$", re.IGNORECASE)
CARNET_REGEX = re.compile(r"^\d{4}-\d{4}[A-Z]$", re.IGNORECASE)
NUP_REGEX = re.compile(r"^[A-Z0-9-]+$", re.IGNORECASE)
CODIGO_TRABAJADOR_REGEX = re.compile(r"^EMP-\d{4,}$", re.IGNORECASE)
GRUPO_REGEX = re.compile(r"^[1-5][MTN][1-9]-[A-Z]{2,4}(-[A-Z0-9]+)?$", re.IGNORECASE)
NOMBRE_REGEX = re.compile(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$")


def calculate_cedula_letter(digits_13: str) -> str:
    """
    Calcula la letra verificadora oficial de la cédula de identidad nicaragüense
    utilizando el algoritmo institucional Módulo 23.
    """
    if not digits_13 or len(digits_13) != 13 or not digits_13.isdigit():
        return ""
    val = int(digits_13)
    rem = val % 23
    return LETTERS_NICA[rem] if rem < len(LETTERS_NICA) else ""


def validate_nombre(nombre: str) -> bool:
    """Valida que el nombre contenga únicamente letras, acentos y espacios."""
    if not nombre or not isinstance(nombre, str):
        return False
    return bool(NOMBRE_REGEX.match(nombre.strip()))


def validate_grupo(grupo: str) -> bool:
    """
    Valida el formato del grupo universitario [ATN-XXX-X]:
    A: Año (1-5), T: Turno (M/T/N), N: Num Grupo (1-9), XXX: Carrera.
    """
    if not grupo or not isinstance(grupo, str):
        return False
    return bool(GRUPO_REGEX.match(grupo.strip()))


def validate_email(email: str) -> bool:
    """
    Valida si una cadena cumple con el formato estándar de correo electrónico.
    
    :param email: Cadena de texto a evaluar.
    :return: True si es un email válido, False en caso contrario.
    """
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_identifier(identifier: str) -> Tuple[bool, str]:
    """
    Determina si un identificador institucional es válido y retorna su tipo.
    
    :param identifier: Cédula, Carné, NUP o Código de Trabajador.
    :return: Tupla (is_valid, tipo_identificador)
    """
    if not identifier or not isinstance(identifier, str):
        return False, "Desconocido"

    clean_id = identifier.strip()

    if EMAIL_REGEX.match(clean_id):
        return True, "Email"
    if CEDULA_REGEX.match(clean_id):
        # Validar la letra verificadora según el algoritmo oficial
        raw_digits = clean_id[:3] + clean_id[4:10] + clean_id[11:15]
        expected_letter = calculate_cedula_letter(raw_digits)
        given_letter = clean_id[-1].upper()
        if expected_letter and given_letter == expected_letter:
            return True, "Cedula"
    if CARNET_REGEX.match(clean_id):
        return True, "Carnet"
    if NUP_REGEX.match(clean_id):
        return True, "NUP"
    if CODIGO_TRABAJADOR_REGEX.match(clean_id):
        return True, "CodigoTrabajador"

    # Si es una cadena alfanumérica limpia mayor a 3 caracteres, permitir como identificador genérico
    if len(clean_id) >= 3 and clean_id.isalnum():
        return True, "Generico"

    return False, "Invalido"


def validate_iso_date(date_str: str) -> bool:
    """
    Valida que una cadena cumpla con el formato de fecha ISO 8601 (YYYY-MM-DD).
    
    :param date_str: Cadena de fecha.
    :return: True si la fecha es válida, False en caso contrario.
    """
    if not date_str or not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_iso_time(time_str: str) -> bool:
    """
    Valida que una cadena cumpla con el formato de hora ISO (HH:MM o HH:MM:SS).
    
    :param time_str: Cadena de hora.
    :return: True si la hora es válida, False en caso contrario.
    """
    if not time_str or not isinstance(time_str, str):
        return False
    clean_time = time_str.strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            datetime.strptime(clean_time, fmt)
            return True
        except ValueError:
            continue
    return False


def sanitize_string(text: Optional[str], max_length: int = 255) -> str:
    """
    Sanitiza una cadena de texto eliminando espacios sobrantes y truncando a la longitud máxima.
    
    :param text: Texto de entrada.
    :param max_length: Longitud máxima permitida.
    :return: Texto sanitizado.
    """
    if not text:
        return ""
    return str(text).strip()[:max_length]
