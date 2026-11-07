"""Migraciones explícitas: no se ejecutan desde una petición web."""
from alembic import context
from sqlalchemy import create_engine
from config import Config
from database import db
import models  # Registra la metadata; no importa ni inicia la aplicación web.


def migrate(connection):
    sqlite = connection.dialect.name == "sqlite"
    try:
        if sqlite:
            # SQLite requiere recrear tablas al modificar nulabilidad. El cambio
            # queda dentro de una transacción y se verifica antes del commit.
            connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
            connection.commit()
            connection.exec_driver_sql("BEGIN IMMEDIATE")
        context.configure(connection=connection, target_metadata=db.metadata, render_as_batch=sqlite)
        with context.begin_transaction():
            context.run_migrations()
        if sqlite:
            if connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall():
                raise RuntimeError("La migración produciría referencias inválidas; se cancela.")
            connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        if sqlite:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")
            connection.commit()


if context.is_offline_mode():
    raise RuntimeError("Esta migración necesita una conexión para inspeccionar el esquema existente.")
provided = context.config.attributes.get("connection")
if provided is not None:
    migrate(provided)
else:
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    with engine.connect() as connection:
        migrate(connection)
