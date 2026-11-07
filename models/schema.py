"""Modelo socioacadémico UNI: 30 tablas basadas en Base de Datosup.
Las excepciones de nulabilidad para perfiles pendientes se documentan en docs/modelo-actualizado.md.
No se consulta ni ejecuta el archivo de Downloads durante la aplicación.
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from database import db

TABLES = {}

paises = sa.Table(
    'paises', db.metadata,
    sa.Column('id_pais', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre', sa.String(100), primary_key=False, nullable=False, unique=True),
    sa.Column('codigo_iso', sa.String(2), primary_key=False, nullable=True, unique=True),
)
TABLES['paises'] = paises

etnias = sa.Table(
    'etnias', db.metadata,
    sa.Column('id_etnia', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre', sa.String(100), primary_key=False, nullable=False, unique=True),
)
TABLES['etnias'] = etnias

departamentos = sa.Table(
    'departamentos', db.metadata,
    sa.Column('id_departamento', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre', sa.String(100), primary_key=False, nullable=False, unique=True),
)
TABLES['departamentos'] = departamentos

municipios = sa.Table(
    'municipios', db.metadata,
    sa.Column('id_municipio', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_departamento', sa.Integer, primary_key=False, nullable=False),
    sa.Column('nombre', sa.String(100), primary_key=False, nullable=False),
    sa.ForeignKeyConstraint(['id_departamento'], ['departamentos.id_departamento'], name='fk_municipio_depto'),
    sa.UniqueConstraint('id_departamento', 'nombre', name='uq_municipio_depto'),
)
TABLES['municipios'] = municipios

centros_educativos = sa.Table(
    'centros_educativos', db.metadata,
    sa.Column('id_centro', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre', sa.String(200), primary_key=False, nullable=False),
    sa.Column('tipo', sa.String(20), primary_key=False, nullable=False),
    sa.Column('id_municipio', sa.Integer, primary_key=False, nullable=True),
    sa.ForeignKeyConstraint(['id_municipio'], ['municipios.id_municipio'], name='fk_centro_municipio'),
    sa.CheckConstraint("tipo IN ('Privado','Estatal')", name='ck_centros_educativos_tipo'),
)
TABLES['centros_educativos'] = centros_educativos

areas_carrera = sa.Table(
    'areas_carrera', db.metadata,
    sa.Column('id_area', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre', sa.String(100), primary_key=False, nullable=False, unique=True),
)
TABLES['areas_carrera'] = areas_carrera

carreras = sa.Table(
    'carreras', db.metadata,
    sa.Column('id_carrera', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre', sa.String(150), primary_key=False, nullable=False, unique=True),
    sa.Column('id_area', sa.Integer, primary_key=False, nullable=False),
    sa.Column('duracion_anios', sa.Integer, primary_key=False, nullable=True),
    sa.ForeignKeyConstraint(['id_area'], ['areas_carrera.id_area'], name='fk_carrera_area'),
    sa.CheckConstraint('duracion_anios BETWEEN 1 AND 10', name='ck_carreras_duracion_anios'),
)
TABLES['carreras'] = carreras

becas = sa.Table(
    'becas', db.metadata,
    sa.Column('id_beca', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre', sa.String(100), primary_key=False, nullable=False, unique=True),
    sa.Column('tipo', sa.String(20), primary_key=False, nullable=False),
    sa.CheckConstraint("tipo IN ('Interna','Externa','Parcial','Completa','Ninguna')", name='ck_becas_tipo'),
)
TABLES['becas'] = becas

estudiantes = sa.Table(
    'estudiantes', db.metadata,
    sa.Column('id_estudiante', sa.Integer, primary_key=True, nullable=False),
    sa.Column('cup', sa.String(20), primary_key=False, nullable=False, unique=True),
    sa.Column('cedula', sa.String(20), primary_key=False, nullable=False, unique=True),
    sa.Column('nombre', sa.String(100), primary_key=False, nullable=False),
    sa.Column('apellido', sa.String(100), primary_key=False, nullable=True),
    sa.Column('fecha_nacimiento', sa.Date, primary_key=False, nullable=True),
    sa.Column('edad', sa.Integer, primary_key=False, nullable=True),
    sa.Column('sexo', sa.String(10), primary_key=False, nullable=False),
    sa.Column('dimension_nacional', sa.String(30), primary_key=False, nullable=True),
    sa.Column('id_pais_origen', sa.Integer, primary_key=False, nullable=True),
    sa.Column('id_etnia', sa.Integer, primary_key=False, nullable=True),
    sa.Column('estado_civil', sa.String(20), primary_key=False, nullable=True),
    sa.Column('hijos', sa.Integer, primary_key=False, nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_pais_origen'], ['paises.id_pais'], name='fk_est_pais'),
    sa.ForeignKeyConstraint(['id_etnia'], ['etnias.id_etnia'], name='fk_est_etnia'),
    sa.CheckConstraint("sexo IN ('Femenino','Masculino','Otro')", name='ck_estudiantes_sexo'),
    sa.CheckConstraint("dimension_nacional IN ('Natural','Nacionalizado','Residente','No Residente')", name='ck_estudiantes_dimension_nacional'),
    sa.CheckConstraint("estado_civil IN ('Soltero','Casado','Union de Hecho','Divorciado','Viudo')", name='ck_estudiantes_estado_civil'),
    sa.CheckConstraint('hijos >= 0', name='ck_estudiantes_hijos'),
    sa.CheckConstraint("fecha_nacimiento IS NULL OR (fecha_nacimiento >= '1900-01-01' AND fecha_nacimiento <= CURRENT_DATE)", name='chk_fecha_nacimiento'),
)
TABLES['estudiantes'] = estudiantes

direcciones_estudiante = sa.Table(
    'direcciones_estudiante', db.metadata,
    sa.Column('id_direccion', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_estudiante', sa.Integer, primary_key=False, nullable=False),
    sa.Column('id_municipio', sa.Integer, primary_key=False, nullable=False),
    sa.Column('comunidad', sa.String(150), primary_key=False, nullable=True),
    sa.Column('direccion_domiciliar', sa.Text, primary_key=False, nullable=True),
    sa.Column('zona', sa.String(10), primary_key=False, nullable=True),
    sa.Column('es_principal', sa.Boolean, primary_key=False, nullable=False, server_default=sa.text('FALSE')),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_estudiante'], ['estudiantes.id_estudiante'], name='fk_dir_estudiante', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_municipio'], ['municipios.id_municipio'], name='fk_dir_municipio'),
    sa.CheckConstraint("zona IN ('Urbano','Rural')", name='ck_direcciones_estudiante_zona'),
)
TABLES['direcciones_estudiante'] = direcciones_estudiante

telefonos_estudiante = sa.Table(
    'telefonos_estudiante', db.metadata,
    sa.Column('id_telefono', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_estudiante', sa.Integer, primary_key=False, nullable=False),
    sa.Column('numero', sa.String(30), primary_key=False, nullable=False),
    sa.Column('tipo', sa.String(15), primary_key=False, nullable=False, server_default=sa.text("'Movil'")),
    sa.Column('es_principal', sa.Boolean, primary_key=False, nullable=False, server_default=sa.text('FALSE')),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_estudiante'], ['estudiantes.id_estudiante'], name='fk_tel_estudiante', ondelete='CASCADE'),
    sa.UniqueConstraint('id_estudiante', 'numero', name='uq_telefono_estudiante'),
    sa.CheckConstraint("tipo IN ('Movil','Fijo','Whatsapp')", name='ck_telefonos_estudiante_tipo'),
)
TABLES['telefonos_estudiante'] = telefonos_estudiante

educacion_previa_estudiante = sa.Table(
    'educacion_previa_estudiante', db.metadata,
    sa.Column('id_educacion', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_estudiante', sa.Integer, primary_key=False, nullable=False),
    sa.Column('id_centro_educativo', sa.Integer, primary_key=False, nullable=True),
    sa.Column('educacion_tecnica', sa.String(200), primary_key=False, nullable=True),
    sa.Column('titulo_obtenido', sa.String(200), primary_key=False, nullable=True),
    sa.Column('anio_graduacion', sa.Integer, primary_key=False, nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_estudiante'], ['estudiantes.id_estudiante'], name='fk_edu_estudiante', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_centro_educativo'], ['centros_educativos.id_centro'], name='fk_edu_centro'),
    sa.CheckConstraint('anio_graduacion IS NULL OR anio_graduacion BETWEEN 1950 AND 2200', name='ck_educacion_previa_estudiante_anio_graduacion'),
)
TABLES['educacion_previa_estudiante'] = educacion_previa_estudiante

matriculas = sa.Table(
    'matriculas', db.metadata,
    sa.Column('id_matricula', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_estudiante', sa.Integer, primary_key=False, nullable=False),
    sa.Column('id_carrera', sa.Integer, primary_key=False, nullable=False),
    sa.Column('periodo_academico', sa.String(20), primary_key=False, nullable=True),
    sa.Column('anio_academico', sa.Integer, primary_key=False, nullable=True),
    sa.Column('modalidad', sa.String(20), primary_key=False, nullable=True),
    sa.Column('turno', sa.String(20), primary_key=False, nullable=True),
    sa.Column('grupo_clase', sa.String(20), primary_key=False, nullable=True),
    sa.Column('id_beca', sa.Integer, primary_key=False, nullable=True),
    sa.Column('estado', sa.String(20), primary_key=False, nullable=False, server_default=sa.text("'Activa'")),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_estudiante'], ['estudiantes.id_estudiante'], name='fk_mat_estudiante'),
    sa.ForeignKeyConstraint(['id_carrera'], ['carreras.id_carrera'], name='fk_mat_carrera'),
    sa.ForeignKeyConstraint(['id_beca'], ['becas.id_beca'], name='fk_mat_beca'),
    sa.UniqueConstraint('id_estudiante', 'periodo_academico', name='uq_matricula_periodo'),
    sa.CheckConstraint('anio_academico BETWEEN 1 AND 10', name='ck_matriculas_anio_academico'),
    sa.CheckConstraint("modalidad IN ('Presencial','Virtual','Mixta')", name='ck_matriculas_modalidad'),
    sa.CheckConstraint("turno IN ('Matutino','Vespertino','Nocturno','Sabatino','Dominical')", name='ck_matriculas_turno'),
    sa.CheckConstraint("estado IN ('Activa','Retirada','Suspendida','Finalizada')", name='ck_matriculas_estado'),
)
TABLES['matriculas'] = matriculas

entidades_receptoras = sa.Table(
    'entidades_receptoras', db.metadata,
    sa.Column('id_entidad', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre', sa.String(150), primary_key=False, nullable=False),
    sa.Column('tipo', sa.String(20), primary_key=False, nullable=False),
    sa.Column('contacto_nombre', sa.String(100), primary_key=False, nullable=True),
    sa.Column('contacto_email', sa.String(120), primary_key=False, nullable=True),
    sa.Column('contacto_telefono', sa.String(30), primary_key=False, nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.CheckConstraint("tipo IN ('Publica','Privada','ONG','Academica')", name='ck_entidades_receptoras_tipo'),
    sa.CheckConstraint(" contacto_email IS NULL OR contacto_email ~* '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$' ", name='ck_entidades_receptoras_contacto_email').ddl_if(dialect="postgresql"),
)
TABLES['entidades_receptoras'] = entidades_receptoras

tutores_docentes = sa.Table(
    'tutores_docentes', db.metadata,
    sa.Column('id_tutor', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre', sa.String(100), primary_key=False, nullable=False),
    sa.Column('apellido', sa.String(100), primary_key=False, nullable=False),
    sa.Column('departamento', sa.String(100), primary_key=False, nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
)
TABLES['tutores_docentes'] = tutores_docentes

supervisores_institucionales = sa.Table(
    'supervisores_institucionales', db.metadata,
    sa.Column('id_supervisor', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre', sa.String(100), primary_key=False, nullable=False),
    sa.Column('apellido', sa.String(100), primary_key=False, nullable=False),
    sa.Column('cargo', sa.String(100), primary_key=False, nullable=True),
    sa.Column('id_entidad', sa.Integer, primary_key=False, nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_entidad'], ['entidades_receptoras.id_entidad'], name='fk_supervisor_entidad'),
    sa.UniqueConstraint('id_supervisor', 'id_entidad', name='uq_supervisor_entidad'),
)
TABLES['supervisores_institucionales'] = supervisores_institucionales

experiencias = sa.Table(
    'experiencias', db.metadata,
    sa.Column('id_experiencia', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_estudiante', sa.Integer, primary_key=False, nullable=False),
    sa.Column('tipo_experiencia', sa.String(20), primary_key=False, nullable=False),
    sa.Column('modalidad', sa.String(20), primary_key=False, nullable=False),
    sa.Column('fecha_inicio', sa.Date, primary_key=False, nullable=False),
    sa.Column('fecha_fin', sa.Date, primary_key=False, nullable=True),
    sa.Column('horas_totales', sa.Integer, primary_key=False, nullable=True),
    sa.Column('estado', sa.String(20), primary_key=False, nullable=False),
    sa.Column('origen', sa.String(30), primary_key=False, nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_estudiante'], ['estudiantes.id_estudiante'], name='fk_exp_estudiante'),
    sa.CheckConstraint("tipo_experiencia IN ('Practica','Pasantia')", name='ck_experiencias_tipo_experiencia'),
    sa.CheckConstraint("modalidad IN ('Presencial','Virtual','Mixta')", name='ck_experiencias_modalidad'),
    sa.CheckConstraint('horas_totales IS NULL OR horas_totales >= 0', name='ck_experiencias_horas_totales'),
    sa.CheckConstraint("estado IN ('Planificada','En Curso','Finalizada','Interrumpida','Cancelada')", name='ck_experiencias_estado'),
    sa.CheckConstraint("origen IN ('Convocatoria','Gestion Institucional','Propuesta Estudiante','Convenio')", name='ck_experiencias_origen'),
    sa.CheckConstraint('fecha_fin IS NULL OR fecha_fin >= fecha_inicio', name='chk_fechas'),
)
TABLES['experiencias'] = experiencias

practicas = sa.Table(
    'practicas', db.metadata,
    sa.Column('id_experiencia', sa.Integer, primary_key=True, nullable=False),
    sa.Column('etapa', sa.String(30), primary_key=False, nullable=False),
    sa.ForeignKeyConstraint(['id_experiencia'], ['experiencias.id_experiencia'], name='fk_practica_exp', ondelete='CASCADE'),
    sa.CheckConstraint("etapa IN ('Familiarizacion','Especializacion','Profesionalizacion')", name='ck_practicas_etapa'),
)
TABLES['practicas'] = practicas

pasantias = sa.Table(
    'pasantias', db.metadata,
    sa.Column('id_experiencia', sa.Integer, primary_key=True, nullable=False),
    sa.Column('tipo', sa.String(30), primary_key=False, nullable=False),
    sa.ForeignKeyConstraint(['id_experiencia'], ['experiencias.id_experiencia'], name='fk_pasantia_exp', ondelete='CASCADE'),
    sa.CheckConstraint("tipo IN ('Academica','Investigacion','Inmersion')", name='ck_pasantias_tipo'),
)
TABLES['pasantias'] = pasantias

asignaciones_experiencia = sa.Table(
    'asignaciones_experiencia', db.metadata,
    sa.Column('id_asignacion', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_experiencia', sa.Integer, primary_key=False, nullable=False),
    sa.Column('rol', sa.String(20), primary_key=False, nullable=False),
    sa.Column('id_tutor', sa.Integer, primary_key=False, nullable=True),
    sa.Column('id_supervisor', sa.Integer, primary_key=False, nullable=True),
    sa.Column('id_entidad', sa.Integer, primary_key=False, nullable=True),
    sa.Column('fecha_desde', sa.Date, primary_key=False, nullable=False, server_default=sa.text('CURRENT_DATE')),
    sa.Column('fecha_hasta', sa.Date, primary_key=False, nullable=True),
    sa.Column('activa', sa.Boolean, primary_key=False, nullable=False, server_default=sa.text('TRUE')),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_experiencia'], ['experiencias.id_experiencia'], name='fk_asig_exp', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_tutor'], ['tutores_docentes.id_tutor'], name='fk_asig_tutor'),
    sa.ForeignKeyConstraint(['id_supervisor', 'id_entidad'], ['supervisores_institucionales.id_supervisor', 'supervisores_institucionales.id_entidad'], name='fk_asig_supervisor_entidad'),
    sa.CheckConstraint("rol IN ('Tutor','Supervisor')", name='ck_asignaciones_experiencia_rol'),
    sa.CheckConstraint(" (rol = 'Tutor' AND id_tutor IS NOT NULL AND id_supervisor IS NULL AND id_entidad IS NULL) OR (rol = 'Supervisor' AND id_supervisor IS NOT NULL AND id_tutor IS NULL AND id_entidad IS NOT NULL) ", name='chk_rol_exclusivo'),
    sa.CheckConstraint('fecha_hasta IS NULL OR fecha_hasta >= fecha_desde', name='chk_vigencia'),
)
TABLES['asignaciones_experiencia'] = asignaciones_experiencia

planes_trabajo = sa.Table(
    'planes_trabajo', db.metadata,
    sa.Column('id_plan', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_experiencia', sa.Integer, primary_key=False, nullable=False),
    sa.Column('version', sa.Integer, primary_key=False, nullable=False, server_default=sa.text('1')),
    sa.Column('estado', sa.String(20), primary_key=False, nullable=False, server_default=sa.text("'Borrador'")),
    sa.Column('objetivos', sa.Text, primary_key=False, nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('fecha_aprobacion', sa.DateTime(timezone=True), primary_key=False, nullable=True),
    sa.Column('aprobado_por_tutor', sa.Integer, primary_key=False, nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_experiencia'], ['experiencias.id_experiencia'], name='fk_plan_exp', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['aprobado_por_tutor'], ['tutores_docentes.id_tutor'], name='fk_plan_aprobador'),
    sa.UniqueConstraint('id_experiencia', 'version', name='uq_plan_version'),
    sa.CheckConstraint('version > 0', name='ck_planes_trabajo_version'),
    sa.CheckConstraint("estado IN ('Borrador','En Revision','Aprobado','Rechazado','Reemplazado')", name='ck_planes_trabajo_estado'),
    sa.CheckConstraint("(estado = 'Aprobado' AND fecha_aprobacion IS NOT NULL) OR (estado <> 'Aprobado')", name='chk_aprobado_consistente'),
)
TABLES['planes_trabajo'] = planes_trabajo

actividades_plan = sa.Table(
    'actividades_plan', db.metadata,
    sa.Column('id_actividad', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_plan', sa.Integer, primary_key=False, nullable=False),
    sa.Column('descripcion', sa.Text, primary_key=False, nullable=False),
    sa.Column('fecha_inicio', sa.Date, primary_key=False, nullable=True),
    sa.Column('fecha_fin', sa.Date, primary_key=False, nullable=True),
    sa.Column('horas_estimadas', sa.Numeric(6,2), primary_key=False, nullable=True),
    sa.Column('estado', sa.String(20), primary_key=False, nullable=False, server_default=sa.text("'Pendiente'")),
    sa.ForeignKeyConstraint(['id_plan'], ['planes_trabajo.id_plan'], name='fk_actividad_plan', ondelete='CASCADE'),
    sa.CheckConstraint("estado IN ('Pendiente','En Curso','Completada')", name='ck_actividades_plan_estado'),
    sa.CheckConstraint('fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio', name='chk_actividad_fechas'),
)
TABLES['actividades_plan'] = actividades_plan

entregables_plan = sa.Table(
    'entregables_plan', db.metadata,
    sa.Column('id_entregable', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_plan', sa.Integer, primary_key=False, nullable=False),
    sa.Column('id_actividad', sa.Integer, primary_key=False, nullable=True),
    sa.Column('nombre', sa.String(200), primary_key=False, nullable=False),
    sa.Column('fecha_entrega_esperada', sa.Date, primary_key=False, nullable=True),
    sa.Column('fecha_entrega_real', sa.Date, primary_key=False, nullable=True),
    sa.Column('estado', sa.String(20), primary_key=False, nullable=False, server_default=sa.text("'Pendiente'")),
    sa.Column('ruta_archivo', sa.String(255), primary_key=False, nullable=True),
    sa.ForeignKeyConstraint(['id_plan'], ['planes_trabajo.id_plan'], name='fk_entregable_plan', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_actividad'], ['actividades_plan.id_actividad'], name='fk_entregable_actividad', ondelete='SET NULL'),
    sa.CheckConstraint("estado IN ('Pendiente','Entregado','Aprobado','Rechazado')", name='ck_entregables_plan_estado'),
)
TABLES['entregables_plan'] = entregables_plan

hitos_plan = sa.Table(
    'hitos_plan', db.metadata,
    sa.Column('id_hito', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_plan', sa.Integer, primary_key=False, nullable=False),
    sa.Column('descripcion', sa.String(200), primary_key=False, nullable=False),
    sa.Column('fecha_hito', sa.Date, primary_key=False, nullable=False),
    sa.Column('cumplido', sa.Boolean, primary_key=False, nullable=False, server_default=sa.text('FALSE')),
    sa.ForeignKeyConstraint(['id_plan'], ['planes_trabajo.id_plan'], name='fk_hito_plan', ondelete='CASCADE'),
)
TABLES['hitos_plan'] = hitos_plan

criterios_evaluacion = sa.Table(
    'criterios_evaluacion', db.metadata,
    sa.Column('id_criterio', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_plan', sa.Integer, primary_key=False, nullable=False),
    sa.Column('descripcion', sa.String(200), primary_key=False, nullable=False),
    sa.Column('peso_porcentaje', sa.Numeric(5,2), primary_key=False, nullable=False),
    sa.ForeignKeyConstraint(['id_plan'], ['planes_trabajo.id_plan'], name='fk_criterio_plan', ondelete='CASCADE'),
    sa.CheckConstraint('peso_porcentaje > 0 AND peso_porcentaje <= 100', name='ck_criterios_evaluacion_peso_porcentaje'),
)
TABLES['criterios_evaluacion'] = criterios_evaluacion

evaluaciones = sa.Table(
    'evaluaciones', db.metadata,
    sa.Column('id_evaluacion', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_experiencia', sa.Integer, primary_key=False, nullable=False),
    sa.Column('id_tutor', sa.Integer, primary_key=False, nullable=True),
    sa.Column('id_supervisor', sa.Integer, primary_key=False, nullable=True),
    sa.Column('calificacion', sa.Numeric(5,2), primary_key=False, nullable=True),
    sa.Column('comentarios', sa.Text, primary_key=False, nullable=True),
    sa.Column('fecha_evaluacion', sa.Date, primary_key=False, nullable=False, server_default=sa.text('CURRENT_DATE')),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_experiencia'], ['experiencias.id_experiencia'], name='fk_eval_exp', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_tutor'], ['tutores_docentes.id_tutor'], name='fk_eval_tutor'),
    sa.ForeignKeyConstraint(['id_supervisor'], ['supervisores_institucionales.id_supervisor'], name='fk_eval_supervisor'),
    sa.CheckConstraint(' calificacion IS NULL OR (calificacion >= 0 AND calificacion <= 100) ', name='ck_evaluaciones_calificacion'),
    sa.CheckConstraint(' (id_tutor IS NOT NULL AND id_supervisor IS NULL) OR (id_supervisor IS NOT NULL AND id_tutor IS NULL) ', name='chk_un_solo_evaluador'),
)
TABLES['evaluaciones'] = evaluaciones

documentos = sa.Table(
    'documentos', db.metadata,
    sa.Column('id_documento', sa.Integer, primary_key=True, nullable=False),
    sa.Column('id_experiencia', sa.Integer, primary_key=False, nullable=False),
    sa.Column('tipo_documento', sa.String(50), primary_key=False, nullable=False),
    sa.Column('ruta_archivo', sa.String(255), primary_key=False, nullable=False),
    sa.Column('fecha_subida', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('estado', sa.String(20), primary_key=False, nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_experiencia'], ['experiencias.id_experiencia'], name='fk_doc_exp', ondelete='CASCADE'),
    sa.CheckConstraint("tipo_documento IN ( 'Carta de Aceptacion','Plan de Trabajo','Informe Final', 'Constancia','Evaluacion','Otro' )", name='ck_documentos_tipo_documento'),
    sa.CheckConstraint("estado IN ('Pendiente','Aprobado','Rechazado')", name='ck_documentos_estado'),
)
TABLES['documentos'] = documentos

usuarios = sa.Table(
    'usuarios', db.metadata,
    sa.Column('id_usuario', sa.Integer, primary_key=True, nullable=False),
    sa.Column('nombre_usuario', sa.String(50), primary_key=False, nullable=False, unique=True),
    sa.Column('email', sa.String(120), nullable=False, unique=True),
    sa.Column('password_hash', sa.String(255), primary_key=False, nullable=False),
    sa.Column('rol', sa.String(20), primary_key=False, nullable=False),
    sa.Column('ruta_imagen', sa.String(255), primary_key=False, nullable=True),
    sa.Column('fecha_creacion', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('activo', sa.Boolean, primary_key=False, nullable=False, server_default=sa.text('TRUE')),
    sa.Column('id_estudiante', sa.Integer, primary_key=False, nullable=True),
    sa.Column('id_tutor', sa.Integer, primary_key=False, nullable=True),
    sa.Column('id_supervisor', sa.Integer, primary_key=False, nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.current_timestamp()),
    sa.ForeignKeyConstraint(['id_estudiante'], ['estudiantes.id_estudiante'], name='fk_usuario_estudiante', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['id_tutor'], ['tutores_docentes.id_tutor'], name='fk_usuario_tutor', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['id_supervisor'], ['supervisores_institucionales.id_supervisor'], name='fk_usuario_supervisor', ondelete='SET NULL'),
    sa.CheckConstraint("nombre_usuario ~ '^[a-zA-Z0-9._-]{4,50}$'", name='ck_usuarios_nombre_usuario').ddl_if(dialect="postgresql"),
    sa.CheckConstraint("rol IN ('Administrador','Coordinador','Tutor','Supervisor','Estudiante','Consulta')", name='ck_usuarios_rol'),
    sa.CheckConstraint(' (CASE WHEN id_estudiante IS NOT NULL THEN 1 ELSE 0 END) + (CASE WHEN id_tutor IS NOT NULL THEN 1 ELSE 0 END) + (CASE WHEN id_supervisor IS NOT NULL THEN 1 ELSE 0 END) <= 1 ', name='chk_usuario_un_vinculo'),
    sa.CheckConstraint(" (rol = 'Estudiante' AND id_estudiante IS NOT NULL AND id_tutor IS NULL AND id_supervisor IS NULL) OR (rol = 'Tutor' AND id_tutor IS NOT NULL AND id_estudiante IS NULL AND id_supervisor IS NULL) OR (rol = 'Supervisor' AND id_supervisor IS NOT NULL AND id_estudiante IS NULL AND id_tutor IS NULL) OR (rol IN ('Administrador','Coordinador','Consulta')) ", name='chk_rol_vinculo'),
)
TABLES['usuarios'] = usuarios

auditoria_cambios = sa.Table(
    'auditoria_cambios', db.metadata,
    sa.Column('id_auditoria', sa.BigInteger().with_variant(sa.Integer, "sqlite"), primary_key=True, nullable=False),
    sa.Column('tabla_afectada', sa.String(63), primary_key=False, nullable=False),
    sa.Column('operacion', sa.String(15), primary_key=False, nullable=False),
    sa.Column('registro_id', sa.BigInteger().with_variant(sa.Integer, "sqlite"), primary_key=False, nullable=False),
    sa.Column('datos_anteriores', sa.JSON().with_variant(pg.JSONB, "postgresql"), primary_key=False, nullable=True),
    sa.Column('datos_nuevos', sa.JSON().with_variant(pg.JSONB, "postgresql"), primary_key=False, nullable=True),
    sa.Column('columnas_modificadas', sa.JSON().with_variant(pg.ARRAY(sa.Text), "postgresql"), primary_key=False, nullable=True),
    sa.Column('id_usuario', sa.Integer, primary_key=False, nullable=True),
    sa.Column('usuario_bd', sa.String(100), primary_key=False, nullable=False, server_default=sa.text("'application'")),
    sa.Column('ip_origen', sa.String(45).with_variant(pg.INET, "postgresql"), primary_key=False, nullable=True),
    sa.Column('user_agent', sa.String(500), primary_key=False, nullable=True),
    sa.Column('fecha_evento', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('transaccion_id', sa.Uuid(as_uuid=False), primary_key=False, nullable=True),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], name='fk_auditoria_usuario', ondelete='SET NULL'),
    sa.CheckConstraint("operacion IN ('INSERT','UPDATE','DELETE','SOFT_DELETE','LOGIN','LOGOUT')", name='ck_auditoria_cambios_operacion'),
)
TABLES['auditoria_cambios'] = auditoria_cambios

auditoria_sesiones = sa.Table(
    'auditoria_sesiones', db.metadata,
    sa.Column('id_sesion_auditoria', sa.BigInteger().with_variant(sa.Integer, "sqlite"), primary_key=True, nullable=False),
    sa.Column('id_usuario', sa.Integer, primary_key=False, nullable=True),
    sa.Column('nombre_usuario_intento', sa.String(50), primary_key=False, nullable=True),
    sa.Column('accion', sa.String(30), primary_key=False, nullable=False),
    sa.Column('resultado', sa.String(10), primary_key=False, nullable=False),
    sa.Column('ip_origen', sa.String(45).with_variant(pg.INET, "postgresql"), primary_key=False, nullable=True),
    sa.Column('user_agent', sa.String(500), primary_key=False, nullable=True),
    sa.Column('detalle', sa.Text, primary_key=False, nullable=True),
    sa.Column('sesion_id', sa.Uuid(as_uuid=False), primary_key=False, nullable=True),
    sa.Column('fecha_evento', sa.DateTime(timezone=True), primary_key=False, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], name='fk_sesion_usuario', ondelete='SET NULL'),
    sa.CheckConstraint("accion IN ( 'LOGIN_OK','LOGIN_FALLIDO','LOGOUT', 'PASSWORD_CHANGE','PASSWORD_RESET', 'ACCOUNT_LOCKED','ACCOUNT_UNLOCKED','ROLE_CHANGED','USUARIO_DESACTIVADO' )", name='ck_auditoria_sesiones_accion'),
    sa.CheckConstraint("resultado IN ('Exito','Fallo')", name='ck_auditoria_sesiones_resultado'),
)
TABLES['auditoria_sesiones'] = auditoria_sesiones

# Restricciones parciales: permiten historial, pero una sola asociación vigente.
sa.Index('uq_direccion_principal', direcciones_estudiante.c.id_estudiante, unique=True, sqlite_where=direcciones_estudiante.c.es_principal.is_(True), postgresql_where=direcciones_estudiante.c.es_principal.is_(True))
sa.Index('uq_telefono_principal', telefonos_estudiante.c.id_estudiante, unique=True, sqlite_where=telefonos_estudiante.c.es_principal.is_(True), postgresql_where=telefonos_estudiante.c.es_principal.is_(True))
sa.Index('uq_asignacion_activa', asignaciones_experiencia.c.id_experiencia, asignaciones_experiencia.c.rol, unique=True, sqlite_where=asignaciones_experiencia.c.activa.is_(True), postgresql_where=asignaciones_experiencia.c.activa.is_(True))
sa.Index('uq_plan_aprobado', planes_trabajo.c.id_experiencia, unique=True, sqlite_where=planes_trabajo.c.estado == 'Aprobado', postgresql_where=planes_trabajo.c.estado == 'Aprobado')
for field in ('id_estudiante', 'id_tutor', 'id_supervisor'):
    sa.Index('uq_usuario_' + field, usuarios.c[field], unique=True)
for table, field in ((usuarios, 'email'), (usuarios, 'nombre_usuario'), (estudiantes, 'cup'), (estudiantes, 'cedula')):
    sa.Index('uq_' + table.name + '_' + field + '_normalizado', sa.func.lower(table.c[field]), unique=True)
sa.Index('idx_auditoria_registro', auditoria_cambios.c.tabla_afectada, auditoria_cambios.c.registro_id)
sa.Index('idx_auditoria_usuario_fecha', auditoria_cambios.c.id_usuario, auditoria_cambios.c.fecha_evento)
sa.Index('idx_sesiones_usuario_fecha', auditoria_sesiones.c.id_usuario, auditoria_sesiones.c.fecha_evento)
