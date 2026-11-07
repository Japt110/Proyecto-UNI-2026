"""Registro de estudiantes sin asignar datos académicos ficticios."""
from alembic import op
import sqlalchemy as sa

revision = "20261105_student_registration"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "personas" not in inspector.get_table_names():
        # Una base vacía se crea con el modelo de la siguiente revisión.
        return

    columns = {c["name"]: c for c in inspector.get_columns("personas")}
    with op.batch_alter_table("personas") as batch:
        for name in ("nombres", "apellidos"):
            if name not in columns:
                batch.add_column(sa.Column(name, sa.String(75), nullable=True))
        batch.alter_column("nombres_apellidos", existing_type=sa.String(150), type_=sa.String(151))
        for name in ("ciudad_residencia_id", "ciudad_procedencia_id", "sede_id"):
            batch.alter_column(name, existing_type=sa.String(36), nullable=True)
    with op.batch_alter_table("estudiantes") as batch:
        for name, length in (("carnet_estudiante", 30), ("area_conocimiento_id", 36),
                             ("carrera", 100), ("ano_academico", 30), ("grupo", 20), ("turno", 30)):
            batch.alter_column(name, existing_type=sa.String(length), nullable=True)
    columns = {c["name"] for c in inspector.get_columns("usuarios")}
    with op.batch_alter_table("usuarios") as batch:
        batch.alter_column("unidad_id", existing_type=sa.String(36), nullable=True)
        if "persona_id" not in columns:
            batch.add_column(sa.Column("persona_id", sa.String(36), nullable=True))
            batch.create_foreign_key("fk_usuarios_persona", "personas", ["persona_id"], ["id"])
            batch.create_unique_constraint("uq_usuarios_persona", ["persona_id"])
    # La BD también impide duplicados normalizados ante solicitudes concurrentes.
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_personas_codigo_normalizado ON personas (upper(numero_unico))")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_personas_cedula_normalizada ON personas (upper(cedula))")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_usuarios_email_normalizado ON usuarios (lower(email))")
    # Mantener esta revisión histórica independiente de los modelos vigentes.
    legacy = sa.MetaData()
    sa.Table("usuarios", legacy, autoload_with=bind)
    sa.Table("auth_sessions", legacy,
             sa.Column("id", sa.String(64), primary_key=True),
             sa.Column("user_id", sa.String(36), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
             sa.Column("expires_at", sa.BigInteger, nullable=False)).create(bind, checkfirst=True)


def downgrade():
    raise RuntimeError("Restaurar la copia previa: volver a NOT NULL descartaría perfiles incompletos.")
