"""Migración SQLite con respaldo y comprobación de cuentas; ejecutar con el servidor detenido."""
from pathlib import Path
import argparse
import datetime
import json
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import make_url
from config import Config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup-dir", type=Path, required=True)
    args = parser.parse_args()
    url = make_url(Config.SQLALCHEMY_DATABASE_URI)
    if url.get_backend_name() != "sqlite" or not url.database or url.database == ":memory:":
        raise SystemExit("Esta herramienta respalda archivos SQLite. Para una base PostgreSQL nueva usar alembic upgrade head.")
    path = Path(url.database).resolve()
    if not path.exists():
        raise SystemExit("No se encontró la base indicada; se cancela para no migrar un archivo equivocado.")
    folder = args.backup_dir.resolve() / datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    folder.mkdir(parents=True, exist_ok=False)
    backup = folder / "app_before.db"
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as src, sqlite3.connect(backup) as dst:
        src.backup(dst)
        if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("El respaldo no pasó la verificación.")
        original = src.execute("SELECT email,password_hash FROM usuarios ORDER BY lower(email)").fetchall()
        if original != dst.execute("SELECT email,password_hash FROM usuarios ORDER BY lower(email)").fetchall():
            raise RuntimeError("Las cuentas del respaldo no coinciden.")
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    cfg = AlembicConfig(str(ROOT / "alembic.ini"))
    cfg.attributes["legacy_backup_verified"] = True
    with engine.connect() as connection:
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")
        report = cfg.attributes.get("migration_report", {"mode": "already_current"})
        updated = connection.exec_driver_sql("SELECT email,password_hash FROM usuarios ORDER BY lower(email)").fetchall()
        assert [(a.lower(), b) for a,b in original] == [tuple(r) for r in updated], "Cambió una cuenta o su contraseña"
        assert not connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
        assert connection.exec_driver_sql("PRAGMA integrity_check").scalar_one() == "ok"
        assert not any("carnet" in c["name"] for t in inspect(connection).get_table_names() for c in inspect(connection).get_columns(t))
    engine.dispose()
    (folder / "migration-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Migración verificada. Cuentas y hashes conservados: {len(original)}. Respaldo: {backup}")
    print(f"Informe: {folder / 'migration-report.json'}")


if __name__ == "__main__":
    main()
