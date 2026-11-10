-- ===============================================================================
-- SISTEMA WEB DE CONTROL DE PASANTÍAS - SCHEMA DDL DEFINITIVO (PostgreSQL)
-- ===============================================================================
-- Generado automáticamente a partir de los modelos relacionales de SQLAlchemy.
-- Total de tablas: 32 tablas relacionales en el esquema 'public'.
-- ===============================================================================

CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE areas_carrera (
	id_area SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id_area)
);

CREATE TABLE becas (
	id_beca SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	tipo VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id_beca)
);

CREATE TABLE departamentos (
	id_departamento SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id_departamento)
);

CREATE TABLE entidades_receptoras (
	id_entidad SERIAL NOT NULL, 
	nombre VARCHAR(150) NOT NULL, 
	tipo VARCHAR(50) NOT NULL, 
	contacto_nombre VARCHAR(100), 
	contacto_email VARCHAR(120), 
	contacto_telefono VARCHAR(30), 
	estado_aprobacion VARCHAR(30), 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_entidad)
);

CREATE TABLE etnias (
	id_etnia SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id_etnia)
);

CREATE TABLE paises (
	id_pais SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	codigo_iso VARCHAR(3) NOT NULL, 
	PRIMARY KEY (id_pais)
);

CREATE TABLE tutores_docentes (
	id_tutor SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	apellido VARCHAR(100) NOT NULL, 
	departamento VARCHAR(100), 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_tutor)
);

CREATE TABLE carreras (
	id_carrera SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	id_area INTEGER NOT NULL, 
	duracion_anios INTEGER NOT NULL, 
	PRIMARY KEY (id_carrera), 
	FOREIGN KEY(id_area) REFERENCES areas_carrera (id_area) ON DELETE RESTRICT
);

CREATE TABLE estudiantes (
	id_estudiante SERIAL NOT NULL, 
	cup VARCHAR(30) NOT NULL, 
	cedula VARCHAR(20) NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	apellido VARCHAR(100) NOT NULL, 
	fecha_nacimiento DATE NOT NULL, 
	edad INTEGER, 
	sexo VARCHAR(20) NOT NULL, 
	dimension_nacional VARCHAR(50), 
	id_pais_origen INTEGER NOT NULL, 
	id_etnia INTEGER NOT NULL, 
	estado_civil VARCHAR(30), 
	hijos INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_estudiante), 
	FOREIGN KEY(id_pais_origen) REFERENCES paises (id_pais) ON DELETE RESTRICT, 
	FOREIGN KEY(id_etnia) REFERENCES etnias (id_etnia) ON DELETE RESTRICT
);

CREATE TABLE municipios (
	id_municipio SERIAL NOT NULL, 
	id_departamento INTEGER NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id_municipio), 
	FOREIGN KEY(id_departamento) REFERENCES departamentos (id_departamento) ON DELETE CASCADE
);

CREATE TABLE supervisores_institucionales (
	id_supervisor SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	apellido VARCHAR(100) NOT NULL, 
	cargo VARCHAR(100), 
	id_entidad INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_supervisor), 
	FOREIGN KEY(id_entidad) REFERENCES entidades_receptoras (id_entidad) ON DELETE RESTRICT
);

CREATE TABLE centros_educativos (
	id_centro SERIAL NOT NULL, 
	nombre VARCHAR(150) NOT NULL, 
	tipo VARCHAR(20) NOT NULL, 
	id_municipio INTEGER NOT NULL, 
	PRIMARY KEY (id_centro), 
	FOREIGN KEY(id_municipio) REFERENCES municipios (id_municipio) ON DELETE RESTRICT
);

CREATE TABLE direcciones_estudiante (
	id_direccion SERIAL NOT NULL, 
	id_estudiante INTEGER NOT NULL, 
	id_municipio INTEGER NOT NULL, 
	comunidad VARCHAR(100), 
	direccion_domiciliar TEXT NOT NULL, 
	zona VARCHAR(20) NOT NULL, 
	es_principal BOOLEAN NOT NULL, 
	PRIMARY KEY (id_direccion), 
	FOREIGN KEY(id_estudiante) REFERENCES estudiantes (id_estudiante) ON DELETE CASCADE, 
	FOREIGN KEY(id_municipio) REFERENCES municipios (id_municipio) ON DELETE RESTRICT
);

CREATE TABLE experiencias (
	id_experiencia SERIAL NOT NULL, 
	id_estudiante INTEGER NOT NULL, 
	tipo_experiencia VARCHAR(30) NOT NULL, 
	modalidad VARCHAR(30) NOT NULL, 
	fecha_inicio DATE NOT NULL, 
	fecha_fin DATE, 
	horas_totales INTEGER NOT NULL, 
	estado VARCHAR(30) NOT NULL, 
	origen VARCHAR(50), 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_experiencia), 
	FOREIGN KEY(id_estudiante) REFERENCES estudiantes (id_estudiante) ON DELETE CASCADE
);

CREATE TABLE matriculas (
	id_matricula SERIAL NOT NULL, 
	id_estudiante INTEGER NOT NULL, 
	id_carrera INTEGER NOT NULL, 
	periodo_academico VARCHAR(30) NOT NULL, 
	anio_academico INTEGER NOT NULL, 
	modalidad VARCHAR(50) NOT NULL, 
	turno VARCHAR(30) NOT NULL, 
	grupo_clase VARCHAR(30), 
	id_beca INTEGER, 
	estado VARCHAR(30) NOT NULL, 
	PRIMARY KEY (id_matricula), 
	FOREIGN KEY(id_estudiante) REFERENCES estudiantes (id_estudiante) ON DELETE CASCADE, 
	FOREIGN KEY(id_carrera) REFERENCES carreras (id_carrera) ON DELETE RESTRICT, 
	FOREIGN KEY(id_beca) REFERENCES becas (id_beca) ON DELETE SET NULL
);

CREATE TABLE telefonos_estudiante (
	id_telefono SERIAL NOT NULL, 
	id_estudiante INTEGER NOT NULL, 
	numero VARCHAR(30) NOT NULL, 
	tipo VARCHAR(30) NOT NULL, 
	es_principal BOOLEAN NOT NULL, 
	PRIMARY KEY (id_telefono), 
	FOREIGN KEY(id_estudiante) REFERENCES estudiantes (id_estudiante) ON DELETE CASCADE
);

CREATE TABLE usuarios (
	id_usuario SERIAL NOT NULL, 
	nombre_usuario VARCHAR(50) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	rol VARCHAR(50) NOT NULL, 
	ruta_imagen VARCHAR(255), 
	fecha_creacion TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	activo BOOLEAN NOT NULL, 
	has_2fa BOOLEAN NOT NULL, 
	id_estudiante INTEGER, 
	id_tutor INTEGER, 
	id_supervisor INTEGER, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_usuario), 
	FOREIGN KEY(id_estudiante) REFERENCES estudiantes (id_estudiante) ON DELETE SET NULL, 
	FOREIGN KEY(id_tutor) REFERENCES tutores_docentes (id_tutor) ON DELETE SET NULL, 
	FOREIGN KEY(id_supervisor) REFERENCES supervisores_institucionales (id_supervisor) ON DELETE SET NULL
);

CREATE TABLE asignaciones_experiencia (
	id_asignacion SERIAL NOT NULL, 
	id_experiencia INTEGER NOT NULL, 
	rol VARCHAR(30) NOT NULL, 
	id_tutor INTEGER, 
	id_supervisor INTEGER, 
	id_entidad INTEGER, 
	fecha_desde DATE NOT NULL, 
	fecha_hasta DATE, 
	activa BOOLEAN NOT NULL, 
	PRIMARY KEY (id_asignacion), 
	FOREIGN KEY(id_experiencia) REFERENCES experiencias (id_experiencia) ON DELETE CASCADE, 
	FOREIGN KEY(id_tutor) REFERENCES tutores_docentes (id_tutor) ON DELETE SET NULL, 
	FOREIGN KEY(id_supervisor) REFERENCES supervisores_institucionales (id_supervisor) ON DELETE SET NULL, 
	FOREIGN KEY(id_entidad) REFERENCES entidades_receptoras (id_entidad) ON DELETE SET NULL
);

CREATE TABLE auditoria_cambios (
	id_auditoria BIGSERIAL NOT NULL, 
	tabla_afectada VARCHAR(100) NOT NULL, 
	operacion VARCHAR(20) NOT NULL, 
	registro_id BIGINT NOT NULL, 
	datos_anteriores JSON, 
	datos_nuevos JSON, 
	columnas_modificadas JSON, 
	id_usuario INTEGER, 
	usuario_bd VARCHAR(100), 
	ip_origen VARCHAR(45), 
	user_agent VARCHAR(255), 
	fecha_evento TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	transaccion_id VARCHAR(36), 
	PRIMARY KEY (id_auditoria), 
	FOREIGN KEY(id_usuario) REFERENCES usuarios (id_usuario) ON DELETE SET NULL
);

CREATE TABLE auditoria_sesiones (
	id_sesion_auditoria BIGSERIAL NOT NULL, 
	id_usuario INTEGER, 
	nombre_usuario_intento VARCHAR(100), 
	accion VARCHAR(50) NOT NULL, 
	resultado VARCHAR(50) NOT NULL, 
	ip_origen VARCHAR(45), 
	user_agent VARCHAR(255), 
	detalle TEXT, 
	sesion_id VARCHAR(36), 
	fecha_evento TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_sesion_auditoria), 
	FOREIGN KEY(id_usuario) REFERENCES usuarios (id_usuario) ON DELETE SET NULL
);

CREATE TABLE documentos (
	id_documento SERIAL NOT NULL, 
	id_estudiante INTEGER, 
	id_experiencia INTEGER, 
	tipo_documento VARCHAR(50) NOT NULL, 
	nombre_original VARCHAR(255), 
	ruta_archivo VARCHAR(255) NOT NULL, 
	tamano_bytes INTEGER, 
	mime_type VARCHAR(100), 
	fecha_subida TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	estado VARCHAR(30) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_documento), 
	FOREIGN KEY(id_estudiante) REFERENCES estudiantes (id_estudiante) ON DELETE CASCADE, 
	FOREIGN KEY(id_experiencia) REFERENCES experiencias (id_experiencia) ON DELETE CASCADE
);

CREATE TABLE educacion_previa_estudiante (
	id_educacion SERIAL NOT NULL, 
	id_estudiante INTEGER NOT NULL, 
	id_centro_educativo INTEGER NOT NULL, 
	educacion_tecnica VARCHAR(150), 
	titulo_obtenido VARCHAR(150) NOT NULL, 
	anio_graduacion INTEGER NOT NULL, 
	PRIMARY KEY (id_educacion), 
	FOREIGN KEY(id_estudiante) REFERENCES estudiantes (id_estudiante) ON DELETE CASCADE, 
	FOREIGN KEY(id_centro_educativo) REFERENCES centros_educativos (id_centro) ON DELETE RESTRICT
);

CREATE TABLE evaluaciones (
	id_evaluacion SERIAL NOT NULL, 
	id_experiencia INTEGER NOT NULL, 
	id_tutor INTEGER, 
	id_supervisor INTEGER, 
	calificacion NUMERIC(5, 2) NOT NULL, 
	comentarios TEXT, 
	fecha_evaluacion DATE NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_evaluacion), 
	CONSTRAINT chk_evaluacion_rango CHECK (calificacion >= 0 AND calificacion <= 100), 
	FOREIGN KEY(id_experiencia) REFERENCES experiencias (id_experiencia) ON DELETE CASCADE, 
	FOREIGN KEY(id_tutor) REFERENCES tutores_docentes (id_tutor) ON DELETE SET NULL, 
	FOREIGN KEY(id_supervisor) REFERENCES supervisores_institucionales (id_supervisor) ON DELETE SET NULL
);

CREATE TABLE ofertas_pasantia (
	id_oferta SERIAL NOT NULL, 
	titulo VARCHAR(150) NOT NULL, 
	tipo VARCHAR(50) NOT NULL, 
	modalidad VARCHAR(30) NOT NULL, 
	duracion VARCHAR(30) NOT NULL, 
	duracion_horas INTEGER NOT NULL, 
	experiencia VARCHAR(50) NOT NULL, 
	sector VARCHAR(50) NOT NULL, 
	ciudad VARCHAR(100) NOT NULL, 
	descripcion TEXT NOT NULL, 
	requisitos TEXT, 
	condiciones VARCHAR(100), 
	cupos INTEGER NOT NULL, 
	estado VARCHAR(30) NOT NULL, 
	id_entidad INTEGER, 
	id_municipio INTEGER, 
	id_carrera INTEGER, 
	id_usuario_creador INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_oferta), 
	FOREIGN KEY(id_entidad) REFERENCES entidades_receptoras (id_entidad) ON DELETE SET NULL, 
	FOREIGN KEY(id_municipio) REFERENCES municipios (id_municipio) ON DELETE SET NULL, 
	FOREIGN KEY(id_carrera) REFERENCES carreras (id_carrera) ON DELETE SET NULL, 
	FOREIGN KEY(id_usuario_creador) REFERENCES usuarios (id_usuario) ON DELETE SET NULL
);

CREATE TABLE pasantias (
	id_experiencia INTEGER NOT NULL, 
	tipo VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id_experiencia), 
	FOREIGN KEY(id_experiencia) REFERENCES experiencias (id_experiencia) ON DELETE CASCADE
);

CREATE TABLE planes_trabajo (
	id_plan SERIAL NOT NULL, 
	id_experiencia INTEGER NOT NULL, 
	version INTEGER NOT NULL, 
	estado VARCHAR(30) NOT NULL, 
	objetivos TEXT, 
	fecha_creacion TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	fecha_aprobacion TIMESTAMP WITHOUT TIME ZONE, 
	aprobado_por_tutor INTEGER, 
	PRIMARY KEY (id_plan), 
	CONSTRAINT uq_plan_experiencia_version UNIQUE (id_experiencia, version), 
	FOREIGN KEY(id_experiencia) REFERENCES experiencias (id_experiencia) ON DELETE CASCADE, 
	FOREIGN KEY(aprobado_por_tutor) REFERENCES tutores_docentes (id_tutor) ON DELETE SET NULL
);

CREATE TABLE practicas (
	id_experiencia INTEGER NOT NULL, 
	etapa VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id_experiencia), 
	FOREIGN KEY(id_experiencia) REFERENCES experiencias (id_experiencia) ON DELETE CASCADE
);

CREATE TABLE actividades_plan (
	id_actividad SERIAL NOT NULL, 
	id_plan INTEGER NOT NULL, 
	descripcion TEXT NOT NULL, 
	fecha_inicio DATE NOT NULL, 
	fecha_fin DATE NOT NULL, 
	horas_estimadas NUMERIC(6, 2) NOT NULL, 
	estado VARCHAR(30) NOT NULL, 
	PRIMARY KEY (id_actividad), 
	FOREIGN KEY(id_plan) REFERENCES planes_trabajo (id_plan) ON DELETE CASCADE
);

CREATE TABLE aplicaciones_oferta (
	id_aplicacion SERIAL NOT NULL, 
	id_oferta INTEGER NOT NULL, 
	id_estudiante INTEGER NOT NULL, 
	fecha_postulacion TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	estado VARCHAR(30) NOT NULL, 
	mensaje TEXT, 
	id_experiencia_generada INTEGER, 
	documentos_compartidos TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id_aplicacion), 
	CONSTRAINT uq_oferta_estudiante_aplicacion UNIQUE (id_oferta, id_estudiante), 
	FOREIGN KEY(id_oferta) REFERENCES ofertas_pasantia (id_oferta) ON DELETE CASCADE, 
	FOREIGN KEY(id_estudiante) REFERENCES estudiantes (id_estudiante) ON DELETE CASCADE, 
	FOREIGN KEY(id_experiencia_generada) REFERENCES experiencias (id_experiencia) ON DELETE SET NULL
);

CREATE TABLE criterios_evaluacion (
	id_criterio SERIAL NOT NULL, 
	id_plan INTEGER NOT NULL, 
	descripcion VARCHAR(255) NOT NULL, 
	peso_porcentaje NUMERIC(5, 2) NOT NULL, 
	PRIMARY KEY (id_criterio), 
	FOREIGN KEY(id_plan) REFERENCES planes_trabajo (id_plan) ON DELETE CASCADE
);

CREATE TABLE hitos_plan (
	id_hito SERIAL NOT NULL, 
	id_plan INTEGER NOT NULL, 
	descripcion VARCHAR(255) NOT NULL, 
	fecha_hito DATE NOT NULL, 
	cumplido BOOLEAN NOT NULL, 
	PRIMARY KEY (id_hito), 
	FOREIGN KEY(id_plan) REFERENCES planes_trabajo (id_plan) ON DELETE CASCADE
);

CREATE TABLE entregables_plan (
	id_entregable SERIAL NOT NULL, 
	id_plan INTEGER NOT NULL, 
	id_actividad INTEGER, 
	nombre VARCHAR(150) NOT NULL, 
	fecha_entrega_esperada DATE NOT NULL, 
	fecha_entrega_real DATE, 
	estado VARCHAR(30) NOT NULL, 
	ruta_archivo VARCHAR(255), 
	PRIMARY KEY (id_entregable), 
	FOREIGN KEY(id_plan) REFERENCES planes_trabajo (id_plan) ON DELETE CASCADE, 
	FOREIGN KEY(id_actividad) REFERENCES actividades_plan (id_actividad) ON DELETE SET NULL
);
