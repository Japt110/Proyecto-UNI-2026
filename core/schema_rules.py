"""Reglas de integridad y auditoría para SQLite local y PostgreSQL.

Las contraseñas y los identificadores secretos de sesión nunca entran en JSON de auditoría.
Los criterios pueden editarse en borrador; deben sumar 100 al aprobar un plan.
"""
import sqlalchemy as sa
from models.schema import TABLES


def install_schema_rules(connection):
    dialect = connection.dialect.name
    if dialect not in {"sqlite", "postgresql"}:
        raise RuntimeError("Motor no soportado: se requiere SQLite o PostgreSQL.")
    sqlite = dialect == "sqlite"

    def execute(sql):
        connection.exec_driver_sql(sql)

    def guard(name, table, operation, condition, message):
        if sqlite:
            execute(f"CREATE TRIGGER IF NOT EXISTS {name} BEFORE {operation} ON {table} WHEN {condition} BEGIN SELECT RAISE(ABORT, '{message}'); END")
        else:
            record = "OLD" if operation == "DELETE" else "NEW"
            execute(f"CREATE OR REPLACE FUNCTION {name}_fn() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF {condition} THEN RAISE EXCEPTION '{message}'; END IF; RETURN {record}; END $$")
            execute(f"DROP TRIGGER IF EXISTS {name} ON {table}")
            execute(f"CREATE TRIGGER {name} BEFORE {operation} ON {table} FOR EACH ROW EXECUTE FUNCTION {name}_fn()")

    for table, subtype in (("practicas", "Practica"), ("pasantias", "Pasantia")):
        for operation in ("INSERT", "UPDATE"):
            guard(f"trg_{table}_{operation.lower()}", table, operation,
                  f"EXISTS (SELECT 1 FROM experiencias WHERE id_experiencia=NEW.id_experiencia AND tipo_experiencia <> '{subtype}')",
                  "El subtipo no coincide con la experiencia")
    guard("trg_exp_subtipo", "experiencias", "UPDATE",
          "(NEW.tipo_experiencia <> 'Practica' AND EXISTS (SELECT 1 FROM practicas WHERE id_experiencia=NEW.id_experiencia)) OR (NEW.tipo_experiencia <> 'Pasantia' AND EXISTS (SELECT 1 FROM pasantias WHERE id_experiencia=NEW.id_experiencia))",
          "No se puede cambiar el tipo de una experiencia con subtipo incompatible")
    guard("trg_exp_finalizada", "experiencias", "DELETE", "OLD.estado='Finalizada'", "No se puede eliminar una experiencia finalizada")
    for operation in ("INSERT", "UPDATE"):
        guard(f"trg_exp_plan_{operation.lower()}", "experiencias", operation,
              "NEW.estado='En Curso' AND NOT EXISTS (SELECT 1 FROM planes_trabajo WHERE id_experiencia=NEW.id_experiencia AND estado='Aprobado')",
              "La experiencia necesita un plan aprobado")
        guard(f"trg_exp_eval_{operation.lower()}", "experiencias", operation,
              "NEW.estado='Finalizada' AND NOT EXISTS (SELECT 1 FROM evaluaciones WHERE id_experiencia=NEW.id_experiencia)",
              "La experiencia necesita una evaluacion")
        guard(f"trg_plan_pesos_{operation.lower()}", "planes_trabajo", operation,
              "NEW.estado='Aprobado' AND COALESCE((SELECT SUM(peso_porcentaje) FROM criterios_evaluacion WHERE id_plan=NEW.id_plan),0) <> 100",
              "Los criterios de un plan aprobado deben sumar 100")
        guard(f"trg_entregable_plan_{operation.lower()}", "entregables_plan", operation,
              "NEW.id_actividad IS NOT NULL AND EXISTS (SELECT 1 FROM actividades_plan WHERE id_actividad=NEW.id_actividad AND id_plan<>NEW.id_plan)",
              "La actividad debe pertenecer al mismo plan")
    for operation in ("INSERT", "UPDATE", "DELETE"):
        refs = ["OLD"] if operation == "DELETE" else ["NEW"] if operation == "INSERT" else ["OLD", "NEW"]
        for ref in refs:
            guard(f"trg_criterio_{operation.lower()}_{ref.lower()}", "criterios_evaluacion", operation,
                  f"EXISTS (SELECT 1 FROM planes_trabajo WHERE id_plan={ref}.id_plan AND estado='Aprobado')",
                  "Cambiar el plan a borrador antes de modificar sus criterios")

    # Edad es un dato derivado: caché al escribir y valor actual calculado en la vista/API.
    age = ("CAST(strftime('%Y','now') AS INTEGER)-CAST(strftime('%Y',NEW.fecha_nacimiento) AS INTEGER)-(strftime('%m-%d','now') < strftime('%m-%d',NEW.fecha_nacimiento))"
           if sqlite else "EXTRACT(YEAR FROM age(CURRENT_DATE, NEW.fecha_nacimiento))::integer")
    if sqlite:
        for op in ("INSERT", "UPDATE OF fecha_nacimiento"):
            suffix = "insert" if op == "INSERT" else "update"
            execute(f"CREATE TRIGGER IF NOT EXISTS trg_edad_{suffix} AFTER {op} ON estudiantes BEGIN UPDATE estudiantes SET edad={age} WHERE id_estudiante=NEW.id_estudiante; END")
    else:
        execute(f"CREATE OR REPLACE FUNCTION fn_edad() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN NEW.edad := {age}; RETURN NEW; END $$")
        execute("DROP TRIGGER IF EXISTS trg_edad ON estudiantes")
        execute("CREATE TRIGGER trg_edad BEFORE INSERT OR UPDATE ON estudiantes FOR EACH ROW EXECUTE FUNCTION fn_edad()")

    audited = set(TABLES) - {"paises", "etnias", "departamentos", "municipios", "centros_educativos", "areas_carrera", "carreras", "becas", "auditoria_cambios", "auditoria_sesiones"}
    for name in sorted(audited):
        table = TABLES[name]
        pk = next(iter(table.primary_key.columns)).name
        fields = [c.name for c in table.c if c.name != "password_hash"]
        if "updated_at" in table.c:
            if sqlite:
                execute(f"CREATE TRIGGER IF NOT EXISTS trg_touch_{name} AFTER UPDATE ON {name} WHEN NEW.updated_at=OLD.updated_at AND NEW.updated_at <> CURRENT_TIMESTAMP BEGIN UPDATE {name} SET updated_at=CURRENT_TIMESTAMP WHERE {pk}=NEW.{pk}; END")
            else:
                execute("CREATE OR REPLACE FUNCTION fn_touch_updated_at() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN NEW.updated_at := CURRENT_TIMESTAMP; RETURN NEW; END $$")
                execute(f"DROP TRIGGER IF EXISTS trg_touch_{name} ON {name}")
                execute(f"CREATE TRIGGER trg_touch_{name} BEFORE UPDATE ON {name} FOR EACH ROW EXECUTE FUNCTION fn_touch_updated_at()")
        for operation in ("INSERT", "UPDATE", "DELETE"):
            ref = "OLD" if operation == "DELETE" else "NEW"
            trigger = f"trg_audit_{name}_{operation.lower()}"
            if sqlite:
                def json_row(row):
                    return "json_object(" + ",".join(f"'{field}',{row}.{field}" for field in fields) + ")"
                old = "NULL" if operation == "INSERT" else json_row("OLD")
                new = "NULL" if operation == "DELETE" else json_row("NEW")
                changed = "NULL"
                if operation == "UPDATE":
                    changed = "(SELECT json_group_array(field) FROM (" + " UNION ALL ".join(f"SELECT '{field}' AS field WHERE NEW.{field} IS NOT OLD.{field}" for field in fields) + "))"
                execute(f"CREATE TRIGGER IF NOT EXISTS {trigger} AFTER {operation} ON {name} BEGIN INSERT INTO auditoria_cambios (tabla_afectada,operacion,registro_id,datos_anteriores,datos_nuevos,columnas_modificadas,usuario_bd) VALUES ('{name}','{operation}',{ref}.{pk},{old},{new},{changed},'application'); END")
            else:
                old = "NULL" if operation == "INSERT" else "to_jsonb(OLD) - 'password_hash'"
                new = "NULL" if operation == "DELETE" else "to_jsonb(NEW) - 'password_hash'"
                changed = "NULL" if operation != "UPDATE" else "ARRAY(SELECT key FROM jsonb_each(to_jsonb(NEW) - 'password_hash') n WHERE n.value IS DISTINCT FROM (to_jsonb(OLD)->n.key))"
                execute(f"CREATE OR REPLACE FUNCTION {trigger}_fn() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN INSERT INTO auditoria_cambios (tabla_afectada,operacion,registro_id,datos_anteriores,datos_nuevos,columnas_modificadas,usuario_bd) VALUES ('{name}','{operation}',{ref}.{pk},{old},{new},{changed},CURRENT_USER); RETURN {ref}; END $$")
                execute(f"DROP TRIGGER IF EXISTS {trigger} ON {name}")
                execute(f"CREATE TRIGGER {trigger} AFTER {operation} ON {name} FOR EACH ROW EXECUTE FUNCTION {trigger}_fn()")

    for field, action in (("password_hash", "PASSWORD_CHANGE"), ("rol", "ROLE_CHANGED"), ("activo", "USUARIO_DESACTIVADO")):
        condition = f"OLD.{field} <> NEW.{field}" + (" AND NEW.activo=FALSE" if field == "activo" else "")
        if sqlite:
            execute(f"CREATE TRIGGER IF NOT EXISTS trg_usuario_{field} AFTER UPDATE ON usuarios WHEN {condition} BEGIN INSERT INTO auditoria_sesiones (id_usuario,accion,resultado) VALUES (NEW.id_usuario,'{action}','Exito'); END")
        else:
            execute(f"CREATE OR REPLACE FUNCTION trg_usuario_{field}_fn() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF {condition} THEN INSERT INTO auditoria_sesiones (id_usuario,accion,resultado) VALUES (NEW.id_usuario,'{action}','Exito'); END IF; RETURN NEW; END $$")
            execute(f"DROP TRIGGER IF EXISTS trg_usuario_{field} ON usuarios")
            execute(f"CREATE TRIGGER trg_usuario_{field} AFTER UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION trg_usuario_{field}_fn()")

    age_view = age.replace("NEW.", "e.")
    execute("DROP VIEW IF EXISTS vw_perfil_estudiante")
    execute(f"""CREATE VIEW vw_perfil_estudiante AS
        SELECT e.id_estudiante, e.cup, e.cedula, e.nombre, e.apellido,
               e.nombre || COALESCE(' ' || e.apellido,'') AS nombre_completo,
               e.fecha_nacimiento, {age_view} AS edad, e.sexo, e.dimension_nacional,
               p.nombre AS pais_origen, et.nombre AS etnia, e.estado_civil, e.hijos,
               d.direccion_domiciliar, d.comunidad, d.zona, m.nombre AS municipio,
               dep.nombre AS departamento, t.numero AS telefono_principal,
               c.nombre AS carrera, a.nombre AS area_carrera, c.duracion_anios,
               ma.anio_academico, ma.periodo_academico, ma.modalidad, ma.turno, ma.grupo_clase,
               b.nombre AS beca, u.nombre_usuario, u.email, u.rol, u.ruta_imagen, u.activo AS usuario_activo
        FROM estudiantes e LEFT JOIN paises p ON p.id_pais=e.id_pais_origen
        LEFT JOIN etnias et ON et.id_etnia=e.id_etnia
        LEFT JOIN direcciones_estudiante d ON d.id_estudiante=e.id_estudiante AND d.es_principal=TRUE
        LEFT JOIN municipios m ON m.id_municipio=d.id_municipio
        LEFT JOIN departamentos dep ON dep.id_departamento=m.id_departamento
        LEFT JOIN telefonos_estudiante t ON t.id_estudiante=e.id_estudiante AND t.es_principal=TRUE
        LEFT JOIN matriculas ma ON ma.id_estudiante=e.id_estudiante AND ma.estado='Activa'
        LEFT JOIN carreras c ON c.id_carrera=ma.id_carrera LEFT JOIN areas_carrera a ON a.id_area=c.id_area
        LEFT JOIN becas b ON b.id_beca=ma.id_beca LEFT JOIN usuarios u ON u.id_estudiante=e.id_estudiante""")
    execute("DROP VIEW IF EXISTS vw_auditoria_publica")
    execute("CREATE VIEW vw_auditoria_publica AS SELECT id_auditoria,tabla_afectada,operacion,registro_id,columnas_modificadas,id_usuario,fecha_evento FROM auditoria_cambios")
    if not sqlite:
        execute("REVOKE UPDATE, DELETE ON auditoria_cambios, auditoria_sesiones FROM PUBLIC")
