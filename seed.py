"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - SCRIPT DE SEMILLA E INICIALIZACIÓN
===============================================================================
Inicializa y puebla la base de datos local (app_local.db) o clúster PostgreSQL:
1. Recrea las 30 tablas del modelo relacional según el diagrama Mermaid.
2. Inserta catálogos base (Países, Etnias, Departamentos, Municipios, Centros Educativos, Carreras, Becas).
3. Inserta estudiantes de prueba con perfil completo (direcciones, teléfonos, trayectoria y matrícula).
4. Inserta entidades receptoras, supervisores institucionales y tutores docentes.
5. Inserta experiencias formativas (Práctica y Pasantía) con planes de trabajo, actividades,
   entregables, hitos, criterios de evaluación y calificaciones.
6. Crea usuarios personificados con credenciales seguras (PBKDF2:SHA256) y bitácoras de auditoría.
===============================================================================
"""

import os
import uuid
from datetime import datetime, timezone, date, timedelta
from app import create_app
from database import db

# Modelos del Sistema Web de Control de Pasantías
from models.catalogos import (
    Pais,
    Etnia,
    Departamento,
    Municipio,
    CentroEducativo,
    AreaCarrera,
    Carrera,
    Beca,
)
from models.perfil_estudiante import (
    Estudiante,
    DireccionEstudiante,
    TelefonoEstudiante,
    EducacionPreviaEstudiante,
    Matricula,
)
from models.actores_externos import (
    EntidadReceptora,
    TutorDocente,
    SupervisorInstitucional,
)
from models.experiencias import (
    Experiencia,
    Practica,
    Pasantia,
    AsignacionExperiencia,
    PlanTrabajo,
    ActividadPlan,
    EntregablePlan,
    HitoPlan,
    CriterioEvaluacion,
    Evaluacion,
    Documento,
)
from models.usuarios_auditoria import (
    Usuario,
    AuditoriaCambios,
    AuditoriaSesiones,
)
from models.ofertas import (
    OfertaPasantia,
    AplicacionOferta,
)

app = create_app()


def seed_database():
    with app.app_context():
        print("[*] Recreando todas las tablas en la base de datos...")
        db.drop_all()
        db.create_all()
        print("[OK] 30 tablas recreadas exitosamente.")

        # ---------------------------------------------------------------------
        # 1. Catálogos: Países y Etnias
        # ---------------------------------------------------------------------
        print("[+] Insertando catálogos de Países y Etnias...")
        p_nic = Pais(nombre="Nicaragua", codigo_iso="NIC")
        p_cri = Pais(nombre="Costa Rica", codigo_iso="CRI")
        p_hnd = Pais(nombre="Honduras", codigo_iso="HND")
        p_slv = Pais(nombre="El Salvador", codigo_iso="SLV")
        p_gtm = Pais(nombre="Guatemala", codigo_iso="GTM")
        db.session.add_all([p_nic, p_cri, p_hnd, p_slv, p_gtm])

        e_mes = Etnia(nombre="Mestizo")
        e_mis = Etnia(nombre="Miskito")
        e_may = Etnia(nombre="Mayangna")
        e_cre = Etnia(nombre="Creol")
        e_ram = Etnia(nombre="Rama")
        e_gar = Etnia(nombre="Garífuna")
        db.session.add_all([e_mes, e_mis, e_may, e_cre, e_ram, e_gar])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 2. Catálogos Geográficos: Departamentos y Municipios
        # ---------------------------------------------------------------------
        print("[+] Insertando Departamentos y Municipios...")
        d_mga = Departamento(nombre="Managua")
        d_leo = Departamento(nombre="León")
        d_est = Departamento(nombre="Estelí")
        d_mat = Departamento(nombre="Matagalpa")
        d_mas = Departamento(nombre="Masaya")
        db.session.add_all([d_mga, d_leo, d_est, d_mat, d_mas])
        db.session.commit()

        m_mga = Municipio(id_departamento=d_mga.id_departamento, nombre="Managua")
        m_tip = Municipio(id_departamento=d_mga.id_departamento, nombre="Tipitapa")
        m_csa = Municipio(id_departamento=d_mga.id_departamento, nombre="Ciudad Sandino")
        m_leo = Municipio(id_departamento=d_leo.id_departamento, nombre="León")
        m_nag = Municipio(id_departamento=d_leo.id_departamento, nombre="Nagarote")
        m_est = Municipio(id_departamento=d_est.id_departamento, nombre="Estelí")
        m_con = Municipio(id_departamento=d_est.id_departamento, nombre="Condega")
        m_mat = Municipio(id_departamento=d_mat.id_departamento, nombre="Matagalpa")
        m_mas = Municipio(id_departamento=d_mas.id_departamento, nombre="Masaya")
        db.session.add_all([m_mga, m_tip, m_csa, m_leo, m_nag, m_est, m_con, m_mat, m_mas])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 3. Catálogos Educativos: Centros Educativos, Áreas, Carreras y Becas
        # ---------------------------------------------------------------------
        print("[+] Insertando Centros Educativos, Áreas de Carrera, Carreras y Becas...")
        c_mg = CentroEducativo(nombre="Instituto Maestro Gabriel", tipo="Estatal", id_municipio=m_mga.id_municipio)
        c_cca = CentroEducativo(nombre="Colegio Centro América", tipo="Privado", id_municipio=m_mga.id_municipio)
        c_ino = CentroEducativo(nombre="Instituto Nacional de Occidente", tipo="Estatal", id_municipio=m_leo.id_municipio)
        c_fle = CentroEducativo(nombre="Instituto Francisco Luis Espinoza", tipo="Estatal", id_municipio=m_est.id_municipio)
        db.session.add_all([c_mg, c_cca, c_ino, c_fle])

        a_tic = AreaCarrera(nombre="Tecnologías de la Información y Comunicación")
        a_ind = AreaCarrera(nombre="Ingeniería Industrial y Procesos")
        a_civ = AreaCarrera(nombre="Construcción y Geotecnia")
        db.session.add_all([a_tic, a_ind, a_civ])
        db.session.commit()

        car_sis = Carrera(nombre="Ingeniería de Sistemas", id_area=a_tic.id_area, duracion_anios=5)
        car_com = Carrera(nombre="Ingeniería en Computación", id_area=a_tic.id_area, duracion_anios=5)
        car_ind = Carrera(nombre="Ingeniería Industrial", id_area=a_ind.id_area, duracion_anios=5)
        car_civ = Carrera(nombre="Ingeniería Civil", id_area=a_civ.id_area, duracion_anios=5)
        db.session.add_all([car_sis, car_com, car_ind, car_civ])

        b_exc = Beca(nombre="Beca de Excelencia Académica", tipo="Completa")
        b_par = Beca(nombre="Beca Parcial de Matrícula", tipo="Parcial")
        b_ali = Beca(nombre="Beca de Alimentación", tipo="Alimenticia")
        b_exo = Beca(nombre="Exoneración Institucional", tipo="Exoneración")
        db.session.add_all([b_exc, b_par, b_ali, b_exo])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 4. Actores Externos: Entidades Receptoras, Tutores y Supervisores
        # ---------------------------------------------------------------------
        print("[+] Insertando Entidades Receptoras, Tutores y Supervisores...")
        ent_banpro = EntidadReceptora(
            nombre="Banco de la Producción (BANPRO)",
            tipo="Privada",
            contacto_nombre="Lic. Denis Morales",
            contacto_email="dmorales@banpro.com.ni",
            contacto_telefono="+505 2255-7000",
        )
        ent_claro = EntidadReceptora(
            nombre="Claro Telecomunicaciones Nicaragua",
            tipo="Privada",
            contacto_nombre="Ing. Karla Vallejos",
            contacto_email="kvallejos@claro.com.ni",
            contacto_telefono="+505 2270-1000",
        )
        ent_mti = EntidadReceptora(
            nombre="Ministerio de Transporte e Infraestructura (MTI)",
            tipo="Pública",
            contacto_nombre="Ing. Francisco Gómez",
            contacto_email="contacto@mti.gob.ni",
            contacto_telefono="+505 2222-3000",
            estado_aprobacion="Aprobada",
        )
        ent_innovatech = EntidadReceptora(
            nombre="InnovaTech Solutions Nicaragua",
            tipo="Privada",
            contacto_nombre="Lic. Maritza Calero",
            contacto_email="mcalero@innovatech.ni",
            contacto_telefono="+505 2288-9900",
            estado_aprobacion="Pendiente_Aprobacion",
        )
        db.session.add_all([ent_banpro, ent_claro, ent_mti, ent_innovatech])
        db.session.commit()

        sup_denis = SupervisorInstitucional(
            nombre="Denis",
            apellido="Morales",
            cargo="Gerente de Infraestructura TI y Seguridad",
            id_entidad=ent_banpro.id_entidad,
        )
        sup_karla = SupervisorInstitucional(
            nombre="Karla",
            apellido="Vallejos",
            cargo="Líder Técnica de Desarrollo de Software",
            id_entidad=ent_claro.id_entidad,
        )
        db.session.add_all([sup_denis, sup_karla])

        tut_ortiz = TutorDocente(
            nombre="José Antonio",
            apellido="Ortiz",
            departamento="Departamento de Computación e Informática",
        )
        tut_rostran = TutorDocente(
            nombre="Elena Patricia",
            apellido="Rostrán",
            departamento="Departamento de Sistemas y Redes",
        )
        db.session.add_all([tut_ortiz, tut_rostran])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 5. Perfil Socio-Académico: Estudiantes, Direcciones, Teléfonos y Matrículas
        # ---------------------------------------------------------------------
        print("[+] Insertando Estudiantes y Ficha Socio-Académica...")
        est1 = Estudiante(
            cup="CUP-2026-001",
            cedula="001-150302-1002A",
            nombre="Carlos Alberto",
            apellido="Mendoza Ruiz",
            fecha_nacimiento=date(2002, 3, 15),
            edad=24,
            sexo="Masculino",
            dimension_nacional="Urbana",
            id_pais_origen=p_nic.id_pais,
            id_etnia=e_mes.id_etnia,
            estado_civil="Soltero",
            hijos=0,
        )
        est2 = Estudiante(
            cup="CUP-2026-002",
            cedula="001-200803-1005B",
            nombre="Ana Sofía",
            apellido="Morales Gómez",
            fecha_nacimiento=date(2003, 8, 20),
            edad=23,
            sexo="Femenino",
            dimension_nacional="Urbana",
            id_pais_origen=p_nic.id_pais,
            id_etnia=e_mes.id_etnia,
            estado_civil="Soltera",
            hijos=0,
        )
        est3 = Estudiante(
            cup="CUP-2026-003",
            cedula="161-100401-1001C",
            nombre="Roberto José",
            apellido="Dávila Silva",
            fecha_nacimiento=date(2001, 4, 10),
            edad=25,
            sexo="Masculino",
            dimension_nacional="Rural",
            id_pais_origen=p_nic.id_pais,
            id_etnia=e_mis.id_etnia,
            estado_civil="Casado",
            hijos=1,
        )
        db.session.add_all([est1, est2, est3])
        db.session.commit()

        # Direcciones
        dir1 = DireccionEstudiante(
            id_estudiante=est1.id_estudiante,
            id_municipio=m_mga.id_municipio,
            comunidad="Colonia Centroamérica",
            direccion_domiciliar="De la Iglesia Fátima 2c al sur, casa #45",
            zona="Urbano",
            es_principal=True,
        )
        dir2 = DireccionEstudiante(
            id_estudiante=est2.id_estudiante,
            id_municipio=m_leo.id_municipio,
            comunidad="Barrio San Juan",
            direccion_domiciliar="Frente al parque San Juan, casa esquinera",
            zona="Urbano",
            es_principal=True,
        )
        db.session.add_all([dir1, dir2])

        # Teléfonos
        tel1 = TelefonoEstudiante(
            id_estudiante=est1.id_estudiante,
            numero="+505 8899-1122",
            tipo="Móvil",
            es_principal=True,
        )
        tel2 = TelefonoEstudiante(
            id_estudiante=est2.id_estudiante,
            numero="+505 8765-4321",
            tipo="WhatsApp",
            es_principal=True,
        )
        db.session.add_all([tel1, tel2])

        # Trayectoria Educativa Previa
        edu1 = EducacionPreviaEstudiante(
            id_estudiante=est1.id_estudiante,
            id_centro_educativo=c_cca.id_centro,
            educacion_tecnica="Técnico Básico en Ofimática",
            titulo_obtenido="Bachiller en Ciencias y Letras",
            anio_graduacion=2019,
        )
        edu2 = EducacionPreviaEstudiante(
            id_estudiante=est2.id_estudiante,
            id_centro_educativo=c_ino.id_centro,
            educacion_tecnica=None,
            titulo_obtenido="Bachiller en Ciencias y Letras",
            anio_graduacion=2020,
        )
        db.session.add_all([edu1, edu2])

        # Matrículas
        mat1 = Matricula(
            id_estudiante=est1.id_estudiante,
            id_carrera=car_sis.id_carrera,
            periodo_academico="I Semestre 2026",
            anio_academico=5,
            modalidad="Regular",
            turno="Matutino",
            grupo_clase="5M1-IS",
            id_beca=b_exc.id_beca,
            estado="Activa",
        )
        mat2 = Matricula(
            id_estudiante=est2.id_estudiante,
            id_carrera=car_com.id_carrera,
            periodo_academico="I Semestre 2026",
            anio_academico=4,
            modalidad="Regular",
            turno="Vespertino",
            grupo_clase="4V1-CO",
            id_beca=b_par.id_beca,
            estado="Activa",
        )
        mat3 = Matricula(
            id_estudiante=est3.id_estudiante,
            id_carrera=car_sis.id_carrera,
            periodo_academico="I Semestre 2026",
            anio_academico=2,
            modalidad="Regular",
            turno="Matutino",
            grupo_clase="2M1-IS",
            id_beca=None,
            estado="Activa",
        )
        db.session.add_all([mat1, mat2, mat3])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 6. Dominio D: Experiencias (Pasantías y Prácticas)
        # ---------------------------------------------------------------------
        print("[+] Insertando Experiencias, Planes, Actividades, Entregables y Evaluaciones...")
        # Experiencia 1: Pasantía en BANPRO
        exp1 = Experiencia(
            id_estudiante=est1.id_estudiante,
            tipo_experiencia="Pasantia",
            modalidad="Hibrido",
            fecha_inicio=date(2026, 2, 1),
            fecha_fin=date(2026, 6, 30),
            horas_totales=360,
            estado="En_Proceso",
            origen="Convocatoria_Institucional",
        )
        db.session.add(exp1)
        db.session.flush()

        pas1 = Pasantia(id_experiencia=exp1.id_experiencia, tipo="Laboral")
        db.session.add(pas1)

        # Asignaciones de la Experiencia 1
        asig_tutor1 = AsignacionExperiencia(
            id_experiencia=exp1.id_experiencia,
            rol="Tutor",
            id_tutor=tut_ortiz.id_tutor,
            id_supervisor=None,
            id_entidad=ent_banpro.id_entidad,
            fecha_desde=date(2026, 2, 1),
            fecha_hasta=None,
            activa=True,
        )
        asig_sup1 = AsignacionExperiencia(
            id_experiencia=exp1.id_experiencia,
            rol="Supervisor",
            id_tutor=None,
            id_supervisor=sup_denis.id_supervisor,
            id_entidad=ent_banpro.id_entidad,
            fecha_desde=date(2026, 2, 1),
            fecha_hasta=None,
            activa=True,
        )
        db.session.add_all([asig_tutor1, asig_sup1])

        # Plan de Trabajo v1
        plan1 = PlanTrabajo(
            id_experiencia=exp1.id_experiencia,
            version=1,
            estado="Aprobado",
            objetivos="Desarrollo e integración de API REST para automatización de conciliaciones financieras.",
            fecha_creacion=datetime(2026, 2, 2, 8, 0, 0, tzinfo=timezone.utc),
            fecha_aprobacion=datetime(2026, 2, 5, 14, 30, 0, tzinfo=timezone.utc),
            aprobado_por_tutor=tut_ortiz.id_tutor,
        )
        db.session.add(plan1)
        db.session.flush()

        # Actividades del Plan
        act1 = ActividadPlan(
            id_plan=plan1.id_plan,
            descripcion="Análisis de requerimientos y modelado de datos para conciliación.",
            fecha_inicio=date(2026, 2, 6),
            fecha_fin=date(2026, 3, 1),
            horas_estimadas=80.0,
            estado="Completada",
        )
        act2 = ActividadPlan(
            id_plan=plan1.id_plan,
            descripcion="Construcción de microservicios en Python/Flask y pruebas unitarias.",
            fecha_inicio=date(2026, 3, 2),
            fecha_fin=date(2026, 5, 15),
            horas_estimadas=160.0,
            estado="En_Progreso",
        )
        db.session.add_all([act1, act2])
        db.session.flush()

        # Entregables del Plan
        entregable1 = EntregablePlan(
            id_plan=plan1.id_plan,
            id_actividad=act1.id_actividad,
            nombre="Documento de Especificación de Requerimientos de Software (SRS)",
            fecha_entrega_esperada=date(2026, 3, 2),
            fecha_entrega_real=date(2026, 3, 1),
            estado="Aprobado",
            ruta_archivo="/uploads/documentos/srs_conciliacion_v1.pdf",
        )
        entregable2 = EntregablePlan(
            id_plan=plan1.id_plan,
            id_actividad=act2.id_actividad,
            nombre="Repositorio Git y reporte de pruebas automatizadas",
            fecha_entrega_esperada=date(2026, 5, 16),
            fecha_entrega_real=None,
            estado="Pendiente",
            ruta_archivo=None,
        )
        db.session.add_all([entregable1, entregable2])

        # Hitos del Plan
        hito1 = HitoPlan(
            id_plan=plan1.id_plan,
            descripcion="Presentación del diseño técnico ante el comité de TI de BANPRO",
            fecha_hito=date(2026, 3, 5),
            cumplido=True,
        )
        hito2 = HitoPlan(
            id_plan=plan1.id_plan,
            descripcion="Despliegue en ambiente Staging / UAT para validación de negocio",
            fecha_hito=date(2026, 5, 20),
            cumplido=False,
        )
        db.session.add_all([hito1, hito2])

        # Criterios de Evaluación
        crit1 = CriterioEvaluacion(
            id_plan=plan1.id_plan,
            descripcion="Calidad técnica del código, arquitectura y buenas prácticas",
            peso_porcentaje=40.0,
        )
        crit2 = CriterioEvaluacion(
            id_plan=plan1.id_plan,
            descripcion="Puntualidad, asistencia y cumplimiento de metas empresariales",
            peso_porcentaje=30.0,
        )
        crit3 = CriterioEvaluacion(
            id_plan=plan1.id_plan,
            descripcion="Informe final escrito y defensa técnica académica",
            peso_porcentaje=30.0,
        )
        db.session.add_all([crit1, crit2, crit3])

        # Evaluación Parcial
        eval1 = Evaluacion(
            id_experiencia=exp1.id_experiencia,
            id_tutor=tut_ortiz.id_tutor,
            id_supervisor=sup_denis.id_supervisor,
            calificacion=95.50,
            comentarios="Excelente desempeño en la etapa de diseño de arquitectura y entrega puntual del SRS.",
            fecha_evaluacion=date(2026, 3, 10),
        )
        db.session.add(eval1)

        # Documentos de Soporte
        doc1 = Documento(
            id_experiencia=exp1.id_experiencia,
            tipo_documento="Convenio_Pasantia",
            ruta_archivo="/uploads/expedientes/convenio_banpro_carlos_mendoza.pdf",
            fecha_subida=datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc),
            estado="Aprobado",
        )
        db.session.add(doc1)

        # Experiencia 2: Práctica Profesional en Claro
        exp2 = Experiencia(
            id_estudiante=est2.id_estudiante,
            tipo_experiencia="Practica",
            modalidad="Presencial",
            fecha_inicio=date(2026, 2, 15),
            fecha_fin=date(2026, 5, 30),
            horas_totales=240,
            estado="En_Proceso",
            origen="Propuesta_Estudiante",
        )
        db.session.add(exp2)
        db.session.flush()

        prac1 = Practica(id_experiencia=exp2.id_experiencia, etapa="Profesional")
        db.session.add(prac1)

        asig_tutor2 = AsignacionExperiencia(
            id_experiencia=exp2.id_experiencia,
            rol="Tutor",
            id_tutor=tut_rostran.id_tutor,
            id_supervisor=None,
            id_entidad=ent_claro.id_entidad,
            fecha_desde=date(2026, 2, 15),
            activa=True,
        )
        asig_sup2 = AsignacionExperiencia(
            id_experiencia=exp2.id_experiencia,
            rol="Supervisor",
            id_tutor=None,
            id_supervisor=sup_karla.id_supervisor,
            id_entidad=ent_claro.id_entidad,
            fecha_desde=date(2026, 2, 15),
            activa=True,
        )
        db.session.add_all([asig_tutor2, asig_sup2])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 7. Subdominio E: Usuarios del Sistema y Auditoría
        # ---------------------------------------------------------------------
        print("[+] Creando cuentas de usuario personificadas...")
        # Administrador
        u_admin = Usuario(
            nombre_usuario="admin",
            email="admin@uni.edu.ni",
            rol="Administrador",
            activo=True,
        )
        u_admin.set_password("admin123")

        # Estudiante
        u_est = Usuario(
            nombre_usuario="carlos.mendoza",
            email="carlos.mendoza@est.uni.edu.ni",
            rol="Estudiante",
            activo=True,
            id_estudiante=est1.id_estudiante,
        )
        u_est.set_password("estudiante123")

        # Tutor Docente
        u_tutor = Usuario(
            nombre_usuario="jose.ortiz",
            email="jose.ortiz@doc.uni.edu.ni",
            rol="Tutor",
            activo=True,
            id_tutor=tut_ortiz.id_tutor,
        )
        u_tutor.set_password("tutor123")

        # Supervisor Institucional
        u_supervisor = Usuario(
            nombre_usuario="denis.morales",
            email="dmorales@banpro.com.ni",
            rol="Supervisor",
            activo=True,
            id_supervisor=sup_denis.id_supervisor,
        )
        u_supervisor.set_password("supervisor123")

        # Estudiante 2do Año (No elegible para pasantías - CU-09)
        u_est3 = Usuario(
            nombre_usuario="roberto.davila",
            email="roberto.davila@est.uni.edu.ni",
            rol="Estudiante",
            activo=True,
            id_estudiante=est3.id_estudiante,
        )
        u_est3.set_password("estudiante123")

        db.session.add_all([u_admin, u_est, u_est3, u_tutor, u_supervisor])
        db.session.commit()

        # Auditoría de Sesión de prueba
        ses_id = str(uuid.uuid4())
        aud_ses = AuditoriaSesiones(
            id_usuario=u_admin.id_usuario,
            nombre_usuario_intento="admin",
            accion="LOGIN",
            resultado="EXITOSO",
            ip_origen="127.0.0.1",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
            detalle="Inicio de sesión administrativo inicial del sistema",
            sesion_id=ses_id,
        )
        db.session.add(aud_ses)

        # Auditoría de Cambios de prueba
        aud_cambio = AuditoriaCambios(
            tabla_afectada="experiencias",
            operacion="INSERT",
            registro_id=exp1.id_experiencia,
            datos_anteriores=None,
            datos_nuevos={
                "id_experiencia": exp1.id_experiencia,
                "id_estudiante": est1.id_estudiante,
                "tipo_experiencia": "Pasantia",
                "estado": "En_Proceso",
            },
            columnas_modificadas=["id_experiencia", "id_estudiante", "tipo_experiencia", "estado"],
            id_usuario=u_admin.id_usuario,
            usuario_bd="sqlite_local",
            ip_origen="127.0.0.1",
            user_agent="Script de Inicialización / Seed",
            transaccion_id=str(uuid.uuid4()),
        )
        db.session.add(aud_cambio)
        db.session.commit()

        # ---------------------------------------------------------------------
        # 8. Ofertas de Pasantías y Aplicaciones Iniciales
        # ---------------------------------------------------------------------
        print("[+] Insertando catálogo de Ofertas de Pasantías y Postulaciones...")
        ofertas_base = [
            OfertaPasantia(
                titulo="Pasantia #1",
                tipo="Académica",
                modalidad="Presencial",
                duracion="160H",
                duracion_horas=160,
                experiencia="Sin experiencia",
                sector="Tecnología",
                ciudad="Managua",
                descripcion="Detalles de la de la pasantia. Prácticas profesionales en desarrollo de software, análisis de sistemas institucionales y administración de bases de datos.",
                cupos=2,
                estado="Activo",
                id_entidad=ent_banpro.id_entidad,
                id_usuario_creador=u_admin.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #2",
                tipo="Académica",
                modalidad="Presencial",
                duracion="160H",
                duracion_horas=160,
                experiencia="Prácticas",
                sector="Química",
                ciudad="Chinandega",
                descripcion="Análisis de laboratorio químico, control de procesos de calidad y seguimiento a normas de bioseguridad industrial.",
                cupos=1,
                estado="Activo",
                id_usuario_creador=u_admin.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #3",
                tipo="Profesional",
                modalidad="Virtual",
                duracion="240H",
                duracion_horas=240,
                experiencia="Junior",
                sector="Industrial",
                ciudad="León",
                descripcion="Optimización de líneas de producción, diseño de rutas de distribución y balanceo de cargas operativas.",
                cupos=2,
                estado="Activo",
                id_usuario_creador=u_admin.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #4",
                tipo="Académica",
                modalidad="Presencial",
                duracion="160H",
                duracion_horas=160,
                experiencia="Sin experiencia",
                sector="Civil",
                ciudad="Estelí",
                descripcion="Levantamiento topográfico asistido, dibujo en AutoCAD y supervisión de mezclas de concreto en sitio.",
                cupos=1,
                estado="Activo",
                id_usuario_creador=u_admin.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #5",
                tipo="Profesional",
                modalidad="Híbrida",
                duracion="320H",
                duracion_horas=320,
                experiencia="Prácticas",
                sector="Eléctrica",
                ciudad="Managua",
                descripcion="Diseño de planos unifilares, mantenimiento preventivo de transformadores y análisis de eficiencia energética.",
                cupos=2,
                estado="Activo",
                id_usuario_creador=u_admin.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #6",
                tipo="Académica",
                modalidad="Presencial",
                duracion="160H",
                duracion_horas=160,
                experiencia="Sin experiencia",
                sector="Tecnología",
                ciudad="Managua",
                descripcion="Soporte técnico a infraestructura de telecomunicaciones, monitoreo de routers Cisco y configuración de VLANs.",
                cupos=3,
                estado="Activo",
                id_entidad=ent_claro.id_entidad,
                id_usuario_creador=u_supervisor.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #7",
                tipo="Académica",
                modalidad="Presencial",
                duracion="160H",
                duracion_horas=160,
                experiencia="Prácticas",
                sector="Industrial",
                ciudad="Matagalpa",
                descripcion="Gestión de inventarios, análisis de mermas y auditoría de almacén en planta de procesamiento agroindustrial.",
                cupos=1,
                estado="Activo",
                id_usuario_creador=u_admin.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #8",
                tipo="Profesional",
                modalidad="Virtual",
                duracion="200H",
                duracion_horas=200,
                experiencia="Junior",
                sector="Química",
                ciudad="Chinandega",
                descripcion="Modelado de procesos de fermentación y análisis espectrofotométrico de muestras químicas.",
                cupos=1,
                estado="Activo",
                id_usuario_creador=u_admin.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #9",
                tipo="Académica",
                modalidad="Presencial",
                duracion="160H",
                duracion_horas=160,
                experiencia="Sin experiencia",
                sector="Tecnología",
                ciudad="Managua",
                descripcion="Desarrollo frontend con estándares modernos HTML5/CSS3/JavaScript y consumo de servicios RESTful.",
                cupos=2,
                estado="Activo",
                id_usuario_creador=u_admin.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #10",
                tipo="Académica",
                modalidad="Presencial",
                duracion="160H",
                duracion_horas=160,
                experiencia="Prácticas",
                sector="Civil",
                ciudad="Juigalpa",
                descripcion="Control de calidad de suelos, ensayos de compresión y asistencia técnica a residentes de obra.",
                cupos=1,
                estado="Activo",
                id_usuario_creador=u_admin.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #11",
                tipo="Profesional",
                modalidad="Híbrida",
                duracion="240H",
                duracion_horas=240,
                experiencia="Junior",
                sector="Industrial",
                ciudad="Managua",
                descripcion="Estudio de tiempos y movimientos, diseño ergonómico de puestos de trabajo y documentación de manuales.",
                cupos=2,
                estado="Activo",
                id_usuario_creador=u_admin.id_usuario,
            ),
            OfertaPasantia(
                titulo="Pasantia #12",
                tipo="Académica",
                modalidad="Presencial",
                duracion="160H",
                duracion_horas=160,
                experiencia="Sin experiencia",
                sector="Tecnología",
                ciudad="Managua",
                descripcion="Seguridad de la información, auditoría de vulnerabilidades web OWASP y gestión de directivas de acceso.",
                cupos=2,
                estado="Activo",
                id_usuario_creador=u_admin.id_usuario,
            ),
        ]
        db.session.add_all(ofertas_base)
        db.session.commit()

        # Insertar una postulación de prueba del estudiante Carlos Mendoza a la Pasantía #1
        ap1 = AplicacionOferta(
            id_oferta=ofertas_base[0].id_oferta,
            id_estudiante=est1.id_estudiante,
            fecha_postulacion=datetime.now(timezone.utc),
            estado="Pendiente",
            mensaje="Me gustaría postularme a esta pasantía para aplicar mis conocimientos en desarrollo de software y bases de datos.",
        )
        db.session.add(ap1)
        db.session.commit()

        print("[OK] ¡Semilla de base de datos completada exitosamente!")
        print("===============================================================================")
        print(" RESUMEN DE DATOS SEMILLA CREADOS:")
        print("===============================================================================")
        print(f" - Catálogos: 5 Países, 6 Etnias, 5 Departamentos, 9 Municipios, 4 Centros, 4 Carreras, 4 Becas")
        print(f" - Perfil Estudiantil: 3 Estudiantes con direcciones, teléfonos, trayectoria y matrículas")
        print(f" - Actores Externos: 3 Entidades Receptoras, 2 Supervisores, 2 Tutores Docentes")
        print(f" - Experiencias: 1 Pasantía (BANPRO) y 1 Práctica Profesional (Claro)")
        print(f" - Planes de Trabajo: 1 Plan v1 con 2 Actividades, 2 Entregables, 2 Hitos y 3 Criterios")
        print(f" - Evaluaciones y Documentos: 1 Evaluación (nota: 95.50) y 1 Convenio firmado")
        print(f" - Usuarios creados:")
        print(f"    * Admin:      admin          | pass: admin123")
        print(f"    * Estudiante: carlos.mendoza | pass: estudiante123")
        print(f"    * Tutor:      jose.ortiz     | pass: tutor123")
        print(f"    * Supervisor: denis.morales  | pass: supervisor123")
        print("===============================================================================")


if __name__ == "__main__":
    seed_database()