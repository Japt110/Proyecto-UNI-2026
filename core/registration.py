"""Validación y creación atómica de cuentas de estudiante."""
from datetime import date
import re
import string
import secrets
import unicodedata

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from database import db
from models.base import Estudiante, Usuario

FIELDS = {"nombres", "apellidos", "sexo", "numero_unico", "cedula", "email", "password"}


class RegistrationInvalid(ValueError):
    def __init__(self, errors):
        self.errors = errors


class RegistrationConflict(ValueError):
    pass


def validate_registration(payload):
    if not isinstance(payload, dict) or set(payload) - FIELDS:
        raise RegistrationInvalid({"form": "Envía únicamente los campos del formulario."})
    data, errors = {}, {}
    for field in FIELDS:
        raw = payload.get(field)
        if not isinstance(raw, str) or not raw:
            errors[field] = "Este campo es obligatorio y debe ser texto."
            continue
        data[field] = raw if field in ("password", "email") else unicodedata.normalize("NFC", raw.strip())
    if errors:
        raise RegistrationInvalid(errors)

    for field in ("nombres", "apellidos"):
        value = data[field]
        valid_chars = all(unicodedata.category(c)[0] in "LM" or c in " '-’" for c in value)
        if not value or len(value) > 75 or not valid_chars or not value[0].isalpha() or not (value[-1].isalpha() or unicodedata.category(value[-1])[0] == "M"):
            errors[field] = "Usa hasta 75 letras, espacios, guiones o apóstrofos."
    if data["sexo"] not in ("Femenino", "Masculino"):
        errors["sexo"] = "Selecciona una opción válida para el sexo."
    code = data["numero_unico"]
    if len(code) > 20 or not re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", code):
        errors["numero_unico"] = "Usa hasta 20 letras o números, separados opcionalmente por guiones."
    match = re.fullmatch(r"([0-9]{3})-([0-9]{2})([0-9]{2})([0-9]{2})-([0-9]{4})([A-Za-z])", data["cedula"])
    if not match:
        errors["cedula"] = "Usa el formato 000-DDMMAA-0000A."
    else:
        try:
            date(2000 + int(match[4]), int(match[3]), int(match[2]))
        except ValueError:
            errors["cedula"] = "La fecha incluida en la cédula no es válida."
    email = data["email"]
    local = email.split("@", 1)[0]
    if (not re.fullmatch(r"[A-Za-z0-9._+\-]+@outlook\.com", email, flags=re.IGNORECASE | re.ASCII)
            or len(local) > 64 or local.startswith(".") or local.endswith(".") or ".." in local):
        errors["email"] = "Ingresa un correo @outlook.com válido, sin espacios ni tildes."
    password = data["password"]
    if not 8 <= len(password) <= 128 or not any(c in string.punctuation for c in password):
        errors["password"] = "Usa de 8 a 128 caracteres y al menos un símbolo estándar, como ! @ # $."
    elif any(unicodedata.category(c) in ("Cc", "Cf", "Cs") for c in password):
        errors["password"] = "La contraseña no admite caracteres de control o invisibles."
    if errors:
        raise RegistrationInvalid(errors)
    data["email"] = email.lower()
    data["numero_unico"] = code.upper()
    data["cedula"] = data["cedula"].upper()
    return data


def register_student(payload):
    data = validate_registration(payload)
    # No asociar automáticamente identidades existentes sin verificar su titularidad.
    exists = Estudiante.query.filter(or_(func.upper(Estudiante.cup) == data["numero_unico"],
                                       func.upper(Estudiante.cedula) == data["cedula"])).first()
    if exists or Usuario.query.filter(func.lower(Usuario.email) == data["email"]).first():
        raise RegistrationConflict()
    try:
        student = Estudiante(cup=data["numero_unico"], cedula=data["cedula"],
                             nombre=data["nombres"], apellido=data["apellidos"], sexo=data["sexo"])
        db.session.add(student)
        db.session.flush()
        # Identificador técnico único: el usuario puede seguir accediendo por CUP o correo.
        user = Usuario(id_estudiante=student.id_estudiante, email=data["email"],
                       nombre_usuario="est_" + secrets.token_hex(16), rol="Estudiante", activo=True)
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return user
    except IntegrityError:
        db.session.rollback()
        raise RegistrationConflict() from None
    except Exception:
        db.session.rollback()
        raise
