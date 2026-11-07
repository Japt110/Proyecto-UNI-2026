"""Integridad del modelo nuevo, auditoría y migración transaccional."""
from datetime import date
from pathlib import Path
import json
import tempfile
import unittest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from alembic import command
from alembic.config import Config
from app import create_app
from database import db
from models.base import Estudiante, Usuario
from models.schema import TABLES as T
from core.model_migration import migrate_model

EXPECTED_TABLES = set("paises etnias departamentos municipios centros_educativos areas_carrera carreras becas estudiantes direcciones_estudiante telefonos_estudiante educacion_previa_estudiante matriculas entidades_receptoras tutores_docentes supervisores_institucionales experiencias practicas pasantias asignaciones_experiencia planes_trabajo actividades_plan entregables_plan hitos_plan criterios_evaluacion evaluaciones documentos usuarios auditoria_cambios auditoria_sesiones".split())


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://",
                               "SQLALCHEMY_ENGINE_OPTIONS": {}, "SQLALCHEMY_BINDS": {},
                               "SECRET_KEY": "test-model-only", "RATE_LIMIT_ENABLED": False,
                               "SESSION_COOKIE_SECURE": False, "CACHE_TYPE": "SimpleCache"})
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.student = Estudiante(cup="SCHEMA-1", cedula="001-010100-1001A", nombre="Prueba", apellido="Modelo", sexo="Femenino")
        db.session.add(self.student)
        db.session.flush()
        self.user = Usuario(nombre_usuario="schema_test", email="schema@outlook.com", rol="Estudiante", id_estudiante=self.student.id_estudiante)
        self.user.set_password("SchemaPass123!")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.ctx.pop()

    def insert(self, name, **values):
        result = db.session.execute(T[name].insert().values(**values))
        return result.inserted_primary_key[0]

    def test_exact_model_tables_and_no_carnet(self):
        inspector = sa.inspect(db.engine)
        self.assertEqual(set(inspector.get_table_names()), EXPECTED_TABLES | {"auth_sessions"})
        self.assertEqual(set(inspector.get_view_names()), {"vw_perfil_estudiante", "vw_auditoria_publica"})
        for table in inspector.get_table_names():
            self.assertFalse(any("carnet" in c["name"] for c in inspector.get_columns(table)))
        self.assertIn("email", T["usuarios"].c)
        self.assertIn("ruta_imagen", T["usuarios"].c)

    def test_audit_keeps_changes_without_password_hash(self):
        self.user.ruta_imagen = "profiles/example.png"
        db.session.commit()
        records = db.session.execute(sa.select(T["auditoria_cambios"]).where(T["auditoria_cambios"].c.tabla_afectada == "usuarios")).mappings().all()
        self.assertGreaterEqual(len(records), 2)
        serialized = json.dumps([dict(r) for r in records], default=str)
        self.assertNotIn(self.user.password_hash, serialized)
        self.assertNotIn("SchemaPass123!", serialized)
        self.assertNotIn('"password_hash"', serialized)
        self.assertIn("profiles/example.png", serialized)

    def test_disabled_account_loses_existing_session(self):
        client = self.app.test_client()
        self.assertEqual(client.post("/api/auth/login", json={"identifier": self.user.email, "password": "SchemaPass123!"}).status_code, 200)
        self.user.activo = False
        db.session.commit()
        self.assertEqual(client.get("/api/auth/me").status_code, 401)
        self.assertEqual(client.post("/api/auth/login", json={"identifier": self.user.email, "password": "SchemaPass123!"}).status_code, 401)
        actions = db.session.execute(sa.select(T["auditoria_sesiones"].c.accion)).scalars().all()
        self.assertIn("LOGIN_OK", actions)
        self.assertIn("USUARIO_DESACTIVADO", actions)
        self.assertIn("LOGIN_FALLIDO", actions)

    def test_profile_uses_actual_user_and_contains_no_demo_or_carnet(self):
        client = self.app.test_client()
        self.assertEqual(client.get("/api/perfil").status_code, 401)
        client.post("/api/auth/login", json={"identifier": self.user.email, "password": "SchemaPass123!"})
        profile = client.get("/api/perfil").json["profile"]
        self.assertEqual(profile["cup"], "SCHEMA-1")
        self.assertEqual(profile["email"], "schema@outlook.com")
        html = client.get("/perfil").get_data(as_text=True)
        self.assertIn("SCHEMA-1", html)
        self.assertNotIn("1999 2526T", html)
        self.assertNotIn("perfil-carnet", html)
        self.assertNotIn("Información de perfil guardada exitosamente", html)
        self.assertEqual(client.get("/api/catalogos").status_code, 200)

    def test_profile_projects_scoped_contact_education_and_enrollment(self):
        from routes.profile_api import profile_data, profile_options
        country = self.insert("paises", nombre="País de prueba")
        ethnicity = self.insert("etnias", nombre="Etnia de prueba")
        department = self.insert("departamentos", nombre="Departamento de prueba")
        other_department = self.insert("departamentos", nombre="Otro departamento")
        city = self.insert("municipios", nombre="Municipio de prueba", id_departamento=department)
        self.insert("municipios", nombre="Municipio ajeno", id_departamento=other_department)
        center = self.insert("centros_educativos", nombre="Centro de prueba", tipo="Estatal")
        area = self.insert("areas_carrera", nombre="Área de prueba")
        career = self.insert("carreras", nombre="Carrera de prueba", id_area=area)
        scholarship = self.insert("becas", nombre="Beca de prueba", tipo="Parcial")
        self.student.id_pais_origen = country
        self.student.id_etnia = ethnicity
        self.student.hijos = 0
        self.student.dimension_nacional = "Natural"
        self.student.estado_civil = "Soltero"
        sid = self.student.id_estudiante
        self.insert("telefonos_estudiante", id_estudiante=sid, numero="88880001", tipo="Whatsapp", es_principal=False)
        self.insert("direcciones_estudiante", id_estudiante=sid, id_municipio=city, comunidad="Comunidad de prueba", zona="Rural", es_principal=True)
        self.insert("educacion_previa_estudiante", id_estudiante=sid, titulo_obtenido="Anterior")
        self.insert("educacion_previa_estudiante", id_estudiante=sid, id_centro_educativo=center, educacion_tecnica="Técnico", titulo_obtenido="Título vigente", anio_graduacion=2025)
        other = self.insert("estudiantes", cup="SCHEMA-2", cedula="001-010100-1002A", nombre="Ajeno", sexo="Masculino")
        self.insert("educacion_previa_estudiante", id_estudiante=other, titulo_obtenido="Dato de otro estudiante")
        self.insert("matriculas", id_estudiante=sid, id_carrera=career, periodo_academico="2026-II", anio_academico=2, modalidad="Mixta", turno="Matutino", grupo_clase="G2", id_beca=scholarship)
        db.session.commit()
        profile = profile_data(self.user)
        expected = dict(id_pais_origen=country, id_etnia=ethnicity, hijos=0, dimension_nacional="Natural",
                        estado_civil="Soltero", tipo_telefono="Whatsapp", telefono_principal=False,
                        id_departamento=department, id_municipio=city, comunidad="Comunidad de prueba", zona="Rural",
                        direccion_principal=True, id_centro_educativo=center, educacion_tecnica="Técnico",
                        titulo_obtenido="Título vigente", anio_graduacion=2025, id_carrera=career,
                        periodo_academico="2026-II", anio=2, modalidad="Mixta", turno="Matutino", grupo_clase="G2", id_beca=scholarship)
        self.assertEqual({key: profile[key] for key in expected}, expected)
        self.assertEqual(profile_options(profile)["municipios"], [(city, "Municipio de prueba")])
        client = self.app.test_client()
        client.post("/api/auth/login", json={"identifier": self.user.email, "password": "SchemaPass123!"})
        html = client.get("/perfil").get_data(as_text=True)
        self.assertIn('value="False" selected>No</option>', html)
        self.assertIn('type="number" value="0"', html)
        self.assertNotIn("Dato de otro estudiante", html)

    def test_age_and_profile_view_calculate_from_birth_date(self):
        self.student.fecha_nacimiento = date(2000, 12, 31)
        db.session.commit()
        age = db.session.execute(sa.text("SELECT edad FROM vw_perfil_estudiante WHERE cup='SCHEMA-1'")).scalar_one()
        self.assertEqual(age, self.student.edad_actual)
        self.assertEqual(db.session.execute(sa.text("SELECT email FROM vw_perfil_estudiante WHERE cup='SCHEMA-1'")).scalar_one(), self.user.email)

    def test_unique_principal_phone_and_foreign_keys(self):
        self.insert("telefonos_estudiante", id_estudiante=self.student.id_estudiante, numero="88880001", es_principal=True)
        db.session.commit()
        with self.assertRaises(IntegrityError):
            self.insert("telefonos_estudiante", id_estudiante=self.student.id_estudiante, numero="88880002", es_principal=True)
        db.session.rollback()
        with self.assertRaises(IntegrityError):
            self.insert("telefonos_estudiante", id_estudiante=999999, numero="88880003")
        db.session.rollback()

    def test_experience_subtypes_plan_criteria_and_evaluation(self):
        exp = self.insert("experiencias", id_estudiante=self.student.id_estudiante, tipo_experiencia="Pasantia", modalidad="Presencial", fecha_inicio=date.today(), estado="Planificada", origen="Convocatoria")
        db.session.commit()
        with self.assertRaises(IntegrityError):
            self.insert("practicas", id_experiencia=exp, etapa="Familiarizacion")
        db.session.rollback()
        self.insert("pasantias", id_experiencia=exp, tipo="Academica")
        plan = self.insert("planes_trabajo", id_experiencia=exp, objetivos="Objetivo de prueba")
        db.session.commit()
        with self.assertRaises(IntegrityError):
            db.session.execute(T["experiencias"].update().where(T["experiencias"].c.id_experiencia==exp).values(estado="En Curso"))
        db.session.rollback()
        self.insert("criterios_evaluacion", id_plan=plan, descripcion="Entrega", peso_porcentaje=60)
        self.insert("criterios_evaluacion", id_plan=plan, descripcion="Evaluación", peso_porcentaje=40)
        db.session.commit()
        db.session.execute(T["planes_trabajo"].update().where(T["planes_trabajo"].c.id_plan==plan).values(estado="Aprobado", fecha_aprobacion=sa.func.current_timestamp()))
        db.session.execute(T["experiencias"].update().where(T["experiencias"].c.id_experiencia==exp).values(estado="En Curso"))
        db.session.commit()
        with self.assertRaises(IntegrityError):
            db.session.execute(T["experiencias"].update().where(T["experiencias"].c.id_experiencia==exp).values(estado="Finalizada"))
        db.session.rollback()
        tutor = self.insert("tutores_docentes", nombre="Tutor", apellido="Prueba")
        self.insert("evaluaciones", id_experiencia=exp, id_tutor=tutor, calificacion=90)
        db.session.execute(T["experiencias"].update().where(T["experiencias"].c.id_experiencia==exp).values(estado="Finalizada"))
        db.session.commit()
        with self.assertRaises(IntegrityError):
            db.session.execute(T["experiencias"].delete().where(T["experiencias"].c.id_experiencia==exp))
        db.session.rollback()

    def test_postgres_ddl_compiles_without_time_dependent_generated_column(self):
        from sqlalchemy.dialects.postgresql import dialect
        for table in db.metadata.sorted_tables:
            sql = str(sa.schema.CreateTable(table).compile(dialect=dialect()))
            self.assertNotIn("GENERATED ALWAYS AS", sql)


class MigrationTests(unittest.TestCase):
    def make_legacy(self, conn):
        definitions = {
            "departamentos": "id TEXT PRIMARY KEY, nombre TEXT",
            "ciudades": "id TEXT PRIMARY KEY, nombre TEXT, departamento_id TEXT",
            "unidades_organizativas": "id TEXT PRIMARY KEY, nombre TEXT",
            "personas": "id TEXT PRIMARY KEY, numero_unico TEXT, cedula TEXT, nombres_apellidos TEXT, nombres TEXT, apellidos TEXT, sexo TEXT, ciudad_residencia_id TEXT",
            "estudiantes": "persona_id TEXT PRIMARY KEY, carrera TEXT, area_conocimiento_id TEXT, ano_academico TEXT, grupo TEXT, turno TEXT, carnet_estudiante TEXT",
            "usuarios": "id TEXT PRIMARY KEY, persona_id TEXT, email TEXT, password_hash TEXT, rol TEXT",
        }
        for name, definition in definitions.items(): conn.exec_driver_sql(f'CREATE TABLE {name} ({definition})')
        conn.exec_driver_sql("INSERT INTO departamentos VALUES ('d','Managua')")
        conn.exec_driver_sql("INSERT INTO ciudades VALUES ('c','Managua','d')")
        conn.exec_driver_sql("INSERT INTO unidades_organizativas VALUES ('a','Ingeniería')")
        conn.exec_driver_sql("INSERT INTO personas VALUES ('p','OLD-1','001-010100-0001A','Nombre histórico completo',NULL,NULL,'Femenino','c')")
        conn.exec_driver_sql("INSERT INTO estudiantes VALUES ('p','Sistemas','a','3er año','G1','Matutino','NO-MIGRAR')")
        conn.exec_driver_sql("INSERT INTO usuarios VALUES ('u','p','Old@Outlook.com','unchanged-hash','Estudiante')")
        conn.commit()

    def test_migrates_data_without_carnet_or_invented_profile_values(self):
        engine = sa.create_engine("sqlite://")
        with engine.connect() as c:
            self.make_legacy(c)
            c.exec_driver_sql("PRAGMA foreign_keys=OFF")
            c.commit()
            c.exec_driver_sql("BEGIN IMMEDIATE")
            report = migrate_model(c, backup_verified=True)
            c.commit()
            user = c.execute(sa.select(T["usuarios"])).mappings().one()
            student = c.execute(sa.select(T["estudiantes"])).mappings().one()
            self.assertEqual(user["email"], "old@outlook.com")
            self.assertEqual(user["password_hash"], "unchanged-hash")
            self.assertEqual(user["id_estudiante"], student["id_estudiante"])
            self.assertEqual(student["nombre"], "Nombre histórico completo")
            self.assertIsNone(student["apellido"])
            self.assertIsNone(student["fecha_nacimiento"])
            self.assertEqual(c.execute(sa.select(T["matriculas"].c.anio_academico)).scalar_one(), 3)
            self.assertEqual(c.execute(sa.select(T["direcciones_estudiante"].c.es_principal)).scalar_one(), True)
            self.assertNotIn("personas", sa.inspect(c).get_table_names())
            self.assertEqual(report["target_counts"]["estudiantes"], 1)
            self.assertEqual(c.exec_driver_sql("PRAGMA foreign_key_check").all(), [])
        engine.dispose()

    def test_failure_rolls_back_legacy_tables_and_data(self):
        engine = sa.create_engine("sqlite://")
        with engine.connect() as c:
            self.make_legacy(c)
            c.exec_driver_sql("INSERT INTO usuarios VALUES ('u2','p','OLD@OUTLOOK.COM','other-hash','Estudiante')")
            c.commit()
            c.exec_driver_sql("PRAGMA foreign_keys=OFF")
            c.commit()
            c.exec_driver_sql("BEGIN IMMEDIATE")
            with self.assertRaises(IntegrityError): migrate_model(c, backup_verified=True)
            c.rollback()
            self.assertIn("personas", sa.inspect(c).get_table_names())
            self.assertEqual(c.exec_driver_sql("SELECT count(*) FROM usuarios").scalar_one(), 2)
            self.assertEqual(c.exec_driver_sql("SELECT carnet_estudiante FROM estudiantes").scalar_one(), "NO-MIGRAR")
        engine.dispose()

    def test_legacy_conversion_requires_backup(self):
        engine = sa.create_engine("sqlite://")
        with engine.connect() as c:
            self.make_legacy(c)
            with self.assertRaisesRegex(RuntimeError, "respaldo"):
                migrate_model(c)
            self.assertIn("personas", sa.inspect(c).get_table_names())
        engine.dispose()

    def test_fresh_alembic_database_and_repeat_upgrade(self):
        cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        engine = sa.create_engine("sqlite://")
        with engine.connect() as c:
            cfg.attributes["connection"] = c
            command.upgrade(cfg, "head")
            command.upgrade(cfg, "head")
            self.assertEqual(set(sa.inspect(c).get_table_names()), EXPECTED_TABLES | {"auth_sessions", "alembic_version"})
            self.assertEqual(c.exec_driver_sql("SELECT version_num FROM alembic_version").scalar_one(), "20261106_socioacademic")
        engine.dispose()
