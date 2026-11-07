"""Modelo socioacadémico de Base de Datosup, con email y sin carné."""
from alembic import op, context
from core.model_migration import migrate_model

revision = "20261106_socioacademic"
down_revision = "20261105_student_registration"
branch_labels = None
depends_on = None


def upgrade():
    config = context.config
    config.attributes["migration_report"] = migrate_model(
        op.get_bind(), backup_verified=config.attributes.get("legacy_backup_verified", False))


def downgrade():
    raise RuntimeError("Restaurar el respaldo previo junto con la versión anterior del código; no descartar datos del modelo nuevo.")
