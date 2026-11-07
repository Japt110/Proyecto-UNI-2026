"""Eventos de autenticación sin contraseñas, cookies ni tokens de sesión."""
from flask import request
from database import db
from models.schema import auditoria_sesiones

def record_access(action, success, user=None, identifier=None):
    db.session.execute(auditoria_sesiones.insert().values(
        id_usuario=user.id if user else None,
        nombre_usuario_intento=(identifier or (user.nombre_usuario if user else ""))[:50] or None,
        accion=action, resultado="Exito" if success else "Fallo",
        ip_origen=request.remote_addr, user_agent=request.user_agent.string[:500],
    ))
