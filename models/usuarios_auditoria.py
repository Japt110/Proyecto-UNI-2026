"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - SUBDOMINIO E: USUARIOS Y AUDITORÍA
===============================================================================
Modelos ORM relacionales para control de acceso, trazabilidad y seguridad:
- Usuario (usuarios): Autenticación polimórfica (Estudiante, Tutor, Supervisor o Admin)
- AuditoriaCambios (auditoria_cambios): Registro histórico forense de DML
- AuditoriaSesiones (auditoria_sesiones): Bitácora de accesos y eventos de autenticación
===============================================================================
"""

from datetime import datetime, timezone
import uuid
from database import db
from core.security import hash_password, verify_password


class Usuario(db.Model):
    """Cuenta de usuario y autenticación con personificación de actores."""
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(50), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), nullable=False)  # ENUM: 'Administrador', 'Estudiante', 'Tutor', 'Supervisor'
    ruta_imagen = db.Column(db.String(255), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    # Personificaciones 1:1 parciales (Foreign Keys opcionales y únicas)
    id_estudiante = db.Column(
        db.Integer,
        db.ForeignKey("estudiantes.id_estudiante", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )
    id_tutor = db.Column(
        db.Integer,
        db.ForeignKey("tutores_docentes.id_tutor", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )
    id_supervisor = db.Column(
        db.Integer,
        db.ForeignKey("supervisores_institucionales.id_supervisor", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relaciones de personificación
    estudiante = db.relationship("Estudiante", back_populates="usuario")
    tutor = db.relationship("TutorDocente", back_populates="usuario")
    supervisor = db.relationship("SupervisorInstitucional", back_populates="usuario")

    # Auditorías
    auditorias_cambios = db.relationship("AuditoriaCambios", back_populates="usuario", lazy="select")
    auditorias_sesiones = db.relationship("AuditoriaSesiones", back_populates="usuario", lazy="select")

    def set_password(self, password: str):
        """Genera y asigna el hash criptográfico seguro PBKDF2:SHA256."""
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Verifica la contraseña ingresada contra el hash seguro."""
        return verify_password(self.password_hash, password)

    def to_dict(self) -> dict:
        """Serializa la cuenta de usuario con los datos de personificación institucional."""
        nombre_completo = self.nombre_usuario
        detalles_actor = {"tipo": self.rol}

        if self.estudiante:
            nom = f"{self.estudiante.nombre or ''} {self.estudiante.apellido or ''}".strip()
            if nom:
                nombre_completo = nom
            
            carrera_nombre = None
            if getattr(self.estudiante, "matriculas", None):
                matriculas = list(self.estudiante.matriculas)
                if matriculas:
                    mat = matriculas[-1]
                    if getattr(mat, "carrera", None):
                        carrera_nombre = mat.carrera.nombre

            detalles_actor = {
                "tipo": "Estudiante",
                "id_estudiante": self.estudiante.id_estudiante,
                "cup": self.estudiante.cup,
                "cedula": self.estudiante.cedula,
                "carrera": carrera_nombre,
                "documentos_count": len(self.estudiante.documentos or []),
            }
        elif self.tutor:
            nom = f"{self.tutor.nombre or ''} {self.tutor.apellido or ''}".strip()
            if nom:
                nombre_completo = nom
            detalles_actor = {
                "tipo": "Tutor",
                "id_tutor": self.tutor.id_tutor,
                "cargo": getattr(self.tutor, "cargo", None) or "Tutor Docente",
            }
        elif self.supervisor:
            nom = f"{self.supervisor.nombre or ''} {self.supervisor.apellido or ''}".strip()
            if nom:
                nombre_completo = nom
            empresa_nombre = None
            if getattr(self.supervisor, "entidad", None):
                empresa_nombre = getattr(self.supervisor.entidad, "nombre", None)
            detalles_actor = {
                "tipo": "Supervisor",
                "id_supervisor": self.supervisor.id_supervisor,
                "cargo": getattr(self.supervisor, "cargo", None) or "Supervisor Institucional",
                "empresa": empresa_nombre,
            }

        return {
            "id_usuario": self.id_usuario,
            "nombre_usuario": self.nombre_usuario,
            "email": self.email,
            "rol": self.rol,
            "activo": bool(self.activo),
            "nombre_completo": nombre_completo,
            "detalles_actor": detalles_actor,
            "fecha_creacion": self.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_creacion else None,
            "ruta_imagen": self.ruta_imagen,
        }

    def __repr__(self):
        return f"<Usuario id={self.id_usuario} user='{self.nombre_usuario}' rol='{self.rol}' activo={self.activo}>"


class AuditoriaCambios(db.Model):
    """Auditoría forense de cambios (INSERT, UPDATE, DELETE) en tablas del sistema."""
    __tablename__ = "auditoria_cambios"

    id_auditoria = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    tabla_afectada = db.Column(db.String(100), nullable=False, index=True)
    operacion = db.Column(db.String(20), nullable=False)  # ENUM: 'INSERT', 'UPDATE', 'DELETE'
    registro_id = db.Column(db.BigInteger, nullable=False, index=True)
    datos_anteriores = db.Column(db.JSON, nullable=True)
    datos_nuevos = db.Column(db.JSON, nullable=True)
    columnas_modificadas = db.Column(db.JSON, nullable=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), nullable=True, index=True)
    usuario_bd = db.Column(db.String(100), nullable=True)
    ip_origen = db.Column(db.String(45), nullable=True)  # Soporte IPv4 e IPv6
    user_agent = db.Column(db.String(255), nullable=True)
    fecha_evento = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    transaccion_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), nullable=True)

    # Relación
    usuario = db.relationship("Usuario", back_populates="auditorias_cambios")

    def __repr__(self):
        return f"<AuditoriaCambios id={self.id_auditoria} tabla='{self.tabla_afectada}' op='{self.operacion}'>"


class AuditoriaSesiones(db.Model):
    """Bitácora de eventos de sesión e intentos de autenticación."""
    __tablename__ = "auditoria_sesiones"

    id_sesion_auditoria = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), nullable=True, index=True)
    nombre_usuario_intento = db.Column(db.String(100), nullable=True)
    accion = db.Column(db.String(50), nullable=False)  # ENUM: 'LOGIN', 'LOGOUT', 'FAILED_LOGIN', 'TOKEN_REFRESH'
    resultado = db.Column(db.String(50), nullable=False)  # ENUM: 'EXITOSO', 'FALLIDO', 'BLOQUEADO'
    ip_origen = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    detalle = db.Column(db.Text, nullable=True)
    sesion_id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), nullable=True)
    fecha_evento = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relación
    usuario = db.relationship("Usuario", back_populates="auditorias_sesiones")

    def __repr__(self):
        return f"<AuditoriaSesiones id={self.id_sesion_auditoria} accion='{self.accion}' res='{self.resultado}'>"
