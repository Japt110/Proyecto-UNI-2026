import os
import uuid
from datetime import datetime, timezone
from app import create_app
from database import db
from models.catalogos import (
    Departamento,
    Ciudad,
    Sede,
    EspacioFisico,
    UnidadOrganizativa,
    TipoActividad,
    EjeLineamiento,
    Lineamiento,
    AccionEstrategica,
)
from models.base import Persona, Estudiante, Trabajador, Usuario
from models.eventos import Actividad, ActividadLineamiento, Asistencia
from core.security import hash_password

app = create_app()

def seed_database():
    with app.app_context():
        # Limpiar datos previos si existieran
        db.drop_all()
        db.create_all()
        print("[OK] Tablas recreadas en app_local.db")

        # Generar nueva marca de versión de semilla para forzar limpieza de caché en navegadores conectados
        os.makedirs("instance", exist_ok=True)
        with open("instance/db_seed.id", "w") as f:
            f.write(str(uuid.uuid4()))

        # ---------------------------------------------------------------------
        # 1. Insertar Catálogos Geográficos (Departamentos y Ciudades)
        # ---------------------------------------------------------------------
        dep_mga = Departamento(nombre="Managua")
        dep_est = Departamento(nombre="Estelí")
        dep_leo = Departamento(nombre="León")
        dep_mat = Departamento(nombre="Matagalpa")
        dep_mas = Departamento(nombre="Masaya")

        db.session.add_all([dep_mga, dep_est, dep_leo, dep_mat, dep_mas])
        db.session.commit()

        c_managua = Ciudad(nombre="Managua", departamento_id=dep_mga.id)
        c_tipitapa = Ciudad(nombre="Tipitapa", departamento_id=dep_mga.id)
        c_esteli = Ciudad(nombre="Estelí", departamento_id=dep_est.id)
        c_condega = Ciudad(nombre="Condega", departamento_id=dep_est.id)
        c_leon = Ciudad(nombre="León", departamento_id=dep_leo.id)
        c_matagalpa = Ciudad(nombre="Matagalpa", departamento_id=dep_mat.id)
        c_masaya = Ciudad(nombre="Masaya", departamento_id=dep_mas.id)

        db.session.add_all([c_managua, c_tipitapa, c_esteli, c_condega, c_leon, c_matagalpa, c_masaya])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 2. Insertar Sedes (vinculadas a su Ciudad correspondiente)
        # ---------------------------------------------------------------------
        sede_rusb = Sede(nombre="Recinto Universitario Simón Bolívar", codigo="RUSB", ciudad_id=c_managua.id)
        sede_rupap = Sede(nombre="Recinto Pedro Aráuz Palacios", codigo="RUPAP", ciudad_id=c_managua.id)
        sede_norte = Sede(nombre="UNI Sede Norte", codigo="UNI-NORTE", ciudad_id=c_esteli.id)
        db.session.add_all([sede_rusb, sede_rupap, sede_norte])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 3. Insertar Espacios Físicos
        # ---------------------------------------------------------------------
        auditorio_1 = EspacioFisico(sede_id=sede_rusb.id, nombre="Auditorio Salomón de la Selva", capacidad=150)
        auditorio_2 = EspacioFisico(sede_id=sede_rupap.id, nombre="Auditorio Central RUPAP", capacidad=200)
        lab_dactic = EspacioFisico(sede_id=sede_rusb.id, nombre="Laboratorio DACTIC", capacidad=100)
        plazoleta = EspacioFisico(sede_id=sede_rusb.id, nombre="Plazoleta Central", capacidad=250)
        biblioteca = EspacioFisico(sede_id=sede_rusb.id, nombre="Biblioteca Central UNI", capacidad=180)
        sala_norte = EspacioFisico(sede_id=sede_norte.id, nombre="Sala de Concurrencia 2", capacidad=80)
        db.session.add_all([auditorio_1, auditorio_2, lab_dactic, plazoleta, biblioteca, sala_norte])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 4. Insertar Unidades Organizativas (Áreas del Conocimiento)
        # ---------------------------------------------------------------------
        edu = UnidadOrganizativa(nombre="Educación", codigo="EDU", nivel_jerarquico="Área")
        art = UnidadOrganizativa(nombre="Artes y humanidades", codigo="ART", nivel_jerarquico="Área")
        csoc = UnidadOrganizativa(nombre="Ciencias sociales, periodismo e información", codigo="CSOC", nivel_jerarquico="Área")
        adm = UnidadOrganizativa(nombre="Administración de empresas y derecho", codigo="ADM", nivel_jerarquico="Área")
        cnat = UnidadOrganizativa(nombre="Ciencias naturales, matemáticas y estadística", codigo="CNAT", nivel_jerarquico="Área")
        tic = UnidadOrganizativa(nombre="Tecnología de la información y la comunicación", codigo="TIC", nivel_jerarquico="Área")
        ing = UnidadOrganizativa(nombre="Ingeniería, industria y construcción", codigo="ING", nivel_jerarquico="Área")
        agr = UnidadOrganizativa(nombre="Agricultura, silvicultura, pesca y veterinaria", codigo="AGR", nivel_jerarquico="Área")
        sal = UnidadOrganizativa(nombre="Salud y bienestar", codigo="SAL", nivel_jerarquico="Área")
        serv = UnidadOrganizativa(nombre="Servicios", codigo="SERV", nivel_jerarquico="Área")

        db.session.add_all([edu, art, csoc, adm, cnat, tic, ing, agr, sal, serv])
        db.session.commit()

        # Reasignación de variables para compatibilidad del script seed.py
        dactic = tic
        fac_ing = ing
        fac_arq = art

        # ---------------------------------------------------------------------
        # 5. Insertar Tipos de Actividad (con Descripción)
        # ---------------------------------------------------------------------
        taller = TipoActividad(nombre="Taller Práctico", descripcion="Sesión interactiva de entrenamiento orientado al desarrollo de competencias técnicas aplicadas.")
        conferencia = TipoActividad(nombre="Conferencia Magistral", descripcion="Exposición académica dictada por expertos en el área sobre avances tecnológicos y científicos.")
        feria = TipoActividad(nombre="Feria Científica", descripcion="Exhibición pública de proyectos de investigación, desarrollo e innovación universitaria.")
        simposio = TipoActividad(nombre="Simposio", descripcion="Reunión de especialistas para discutir y debatir sobre una temática científica determinada.")
        db.session.add_all([taller, conferencia, feria, simposio])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 6. Insertar Ejes, Lineamientos y Acciones (Estrategia Nacional de Educación 2026)
        # ---------------------------------------------------------------------
        ejes_data = [
            ("Eje 1", "Educación para la Vida", [
                ("1.1", "Desarrollo de competencias y habilidades prácticas para la vida y el trabajo."),
                ("1.2", "Promover programas de formación orientados al desarrollo productivo y comunitario.")
            ]),
            ("Eje 2", "Educación en Valores", [
                ("2.1", "Fortalecer valores de civismo, ética profesional, liderazgo y valores universitarios."),
                ("2.2", "Fomentar el respeto, la tolerancia y la convivencia armoniosa en la comunidad educativa.")
            ]),
            ("Eje 3", "Educación Creativa", [
                ("3.1", "Impulsar el pensamiento crítico, la creatividad y la resolución de problemas."),
                ("3.2", "Fomentar metodologías de aprendizaje activas e innovadoras.")
            ]),
            ("Eje 4", "Educación Artística y Cultural", [
                ("4.1", "Promover la apreciación artística y la expresión cultural."),
                ("4.2", "Preservar y difundir el patrimonio cultural e histórico nacional.")
            ]),
            ("Eje 5", "Historia e Identidad Nacional", [
                ("5.1", "Fortalecer el estudio de la historia patria y la soberanía."),
                ("5.2", "Consolidar el sentido de pertenencia e identidad cultural nicaragüense.")
            ]),
            ("Eje 6", "Ambiente y Naturaleza", [
                ("6.1", "Fomentar la educación ambiental y el cuidado de los recursos naturales."),
                ("6.2", "Implementar prácticas de campus verde y desarrollo sostenible.")
            ]),
            ("Eje 7", "Cambio Climático", [
                ("7.1", "Desarrollar capacidades de resiliencia y adaptación ante el cambio climático."),
                ("7.2", "Promover investigaciones sobre mitigación y gestión del riesgo climático.")
            ]),
            ("Eje 8", "Educación Física y Deportiva", [
                ("8.1", "Fomentar la práctica del deporte y la actividad física regular."),
                ("8.2", "Promover estilos de vida saludables y recreación sana.")
            ]),
            ("Eje 9", "Educación Especial Incluyente", [
                ("9.1", "Garantizar la inclusión y accesibilidad para personas con discapacidad."),
                ("9.2", "Desarrollar recursos pedagógicos adaptados a las necesidades especiales.")
            ]),
            ("Eje 10", "Ciencias", [
                ("10.1", "Fortalecer la formación científica y experimental en todas las disciplinas."),
                ("10.2", "Promover la divulgación científica y tecnológica en la sociedad.")
            ]),
            ("Eje 11", "Investigación e Innovación", [
                ("11.1", "Impulsar proyectos de investigación e innovación tecnológica aplicados."),
                ("11.2", "Promover prototipos y ferias del conocimiento para la transferencia de soluciones.")
            ]),
            ("Eje 12", "Cobertura Amplia, con Inclusión y Equidad Modalidad Presencial y Virtual", [
                ("12.1", "Expandir la cobertura educativa a través de modalidades flexibles y virtuales."),
                ("12.2", "Garantizar el acceso equitativo a la educación de calidad para sectores vulnerables.")
            ]),
            ("Eje 13", "Calidad Educativa", [
                ("13.1", "Asegurar la mejora continua de los currículos y planes de estudio."),
                ("13.2", "Implementar sistemas de evaluación y acreditación de la calidad académica.")
            ]),
            ("Eje 14", "Formación Docente", [
                ("14.1", "Capacitar permanentemente al profesorado en didáctica y nuevas tecnologías."),
                ("14.2", "Promover la investigación educativa y el desarrollo profesional docente.")
            ]),
            ("Eje 15", "Fortalecimiento Institucional", [
                ("15.1", "Optimizar la gestión administrativa y los procesos institucionales."),
                ("15.2", "Implementar tecnologías de la información para la transparencia y eficiencia.")
            ]),
            ("Eje 16", "Infraestructura y Equipamiento", [
                ("16.1", "Mejorar la infraestructura física y laboratorios de la universidad."),
                ("16.2", "Garantizar el equipamiento tecnológico adecuado para el aprendizaje moderno.")
            ])
        ]

        lineamiento_1_1 = None
        lineamiento_1_2 = None
        lineamiento_2_1 = None
        lineamiento_2_2 = None
        lineamiento_3_1 = None

        for num_oficial, nombre, lins in ejes_data:
            eje = EjeLineamiento(
                numero_oficial=num_oficial,
                nombre=nombre,
                descripcion=f"Eje de la Estrategia Nacional de Educación: {nombre}"
            )
            db.session.add(eje)
            db.session.commit()

            for sub_num, desc in lins:
                lin = Lineamiento(
                    eje_id=eje.id,
                    numero_oficial=sub_num,
                    descripcion=desc
                )
                db.session.add(lin)
                db.session.commit()

                if sub_num == "1.1":
                    lineamiento_1_1 = lin
                elif sub_num == "1.2":
                    lineamiento_1_2 = lin
                elif sub_num == "11.1":
                    lineamiento_2_1 = lin
                elif sub_num == "11.2":
                    lineamiento_2_2 = lin
                elif sub_num == "15.1":
                    lineamiento_3_1 = lin

        # Seguridad de mapeo para evitar errores de referencia en el resto del seed script
        if not lineamiento_2_1: lineamiento_2_1 = lineamiento_1_1
        if not lineamiento_3_1: lineamiento_3_1 = lineamiento_1_1

        accion_1 = AccionEstrategica(
            lineamiento_id=lineamiento_2_1.id,
            descripcion="Desarrollar ferias anuales de proyectos científicos multidisciplinarios con impacto social."
        )
        accion_2 = AccionEstrategica(
            lineamiento_id=lineamiento_3_1.id,
            descripcion="Capacitar a la comunidad universitaria en el uso ético y efectivo de herramientas de Inteligencia Artificial."
        )
        db.session.add_all([accion_1, accion_2])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 7. Insertar Usuarios de Sistema
        # ---------------------------------------------------------------------
        user_encargado = Usuario(
            id="00000000-0000-4000-a000-000000000001",
            unidad_id=dactic.id,
            email="encargado@uni.edu.ni",
            password_hash=hash_password("admin123"),
            rol="Encargado"
        )
        user_rector = Usuario(
            id="00000000-0000-4000-a000-000000000002",
            unidad_id=dactic.id,
            email="rector@uni.edu.ni",
            password_hash=hash_password("rector123"),
            rol="Rector"
        )
        db.session.add_all([user_encargado, user_rector])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 8. Insertar Personas de Prueba (con Ciudad de Residencia y Procedencia)
        # ---------------------------------------------------------------------
        p_est = Persona(
            numero_unico="NUP-2026-001",
            cedula="001-030704-1067H",
            nombres_apellidos="Aaron David Díaz Martínez",
            sexo="Masculino",
            ciudad_residencia_id=c_managua.id,
            ciudad_procedencia_id=c_esteli.id,
            sede_id=sede_rusb.id
        )
        db.session.add(p_est)
        db.session.commit()

        estudiante = Estudiante(
            persona_id=p_est.id,
            carnet_estudiante="2021-0001U",
            area_conocimiento_id=fac_ing.id,
            carrera="Ingeniería Mecánica",
            ano_academico="Séptimo Año",
            grupo="1M1-ME",
            turno="Diurno"
        )

        p_trab = Persona(
            numero_unico="NUP-2026-002",
            cedula="001-150880-0002A",
            nombres_apellidos="Dr. Roberto Morales",
            sexo="Masculino",
            ciudad_residencia_id=c_managua.id,
            ciudad_procedencia_id=c_leon.id,
            sede_id=sede_rusb.id
        )
        db.session.add(p_trab)
        db.session.commit()

        trabajador = Trabajador(
            persona_id=p_trab.id,
            codigo_trabajador="EMP-9082",
            unidad_id=dactic.id,
            cargo="Docente Titular / Coordinador",
            condicion_laboral="Planta"
        )

        db.session.add_all([estudiante, trabajador])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 9. Insertar Actividades
        # ---------------------------------------------------------------------
        actividades_seed = [
            # ACTIVOS
            Actividad(
                id=str(uuid.uuid4()),
                codigo_actividad="ACT-2026-001",
                nombre="Proyectos científicos de investigación en TI",
                tipo_actividad_id=feria.id,
                unidad_responsable_id=dactic.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=auditorio_2.id,
                proposito="Exposición anual de proyectos de investigación científica de docentes y estudiantes en tecnologías de la información.",
                fecha_inicio="2026-08-15",
                fecha_fin="2026-08-18",
                hora_inicio="08:00:00",
                hora_fin="16:00:00",
                is_synced=1,
                created_offline=0,
                updated_at=datetime.now(timezone.utc).isoformat()
            ),
            Actividad(
                id=str(uuid.uuid4()),
                codigo_actividad="ACT-2026-002",
                nombre="Feria de innovación robótica y software embebido",
                tipo_actividad_id=feria.id,
                unidad_responsable_id=dactic.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=lab_dactic.id,
                proposito="Feria de innovación robótica y desarrollo de software embebido aplicado a la industria nacional.",
                fecha_inicio="2026-08-20",
                fecha_fin="2026-08-22",
                hora_inicio="09:00:00",
                hora_fin="15:00:00",
                is_synced=1,
                created_offline=0,
                updated_at=datetime.now(timezone.utc).isoformat()
            ),
            # PROGRAMADOS
            Actividad(
                id=str(uuid.uuid4()),
                codigo_actividad="ACT-2026-003",
                nombre="Simposio sobre inteligencia artificial aplicada",
                tipo_actividad_id=simposio.id,
                unidad_responsable_id=dactic.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=sala_norte.id,
                proposito="Simposio sobre inteligencia artificial aplicada a la eficiencia energética en construcciones civiles.",
                fecha_inicio="2026-09-05",
                fecha_fin="2026-09-05",
                hora_inicio="10:00:00",
                hora_fin="14:00:00",
                is_synced=1,
                created_offline=0,
                updated_at=datetime.now(timezone.utc).isoformat()
            ),
            Actividad(
                id=str(uuid.uuid4()),
                codigo_actividad="ACT-2026-004",
                nombre="Encuentro universitario de investigación ambiental",
                tipo_actividad_id=conferencia.id,
                unidad_responsable_id=fac_ing.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=plazoleta.id,
                proposito="Encuentro universitario de investigación ambiental y desarrollo sostenible.",
                fecha_inicio="2026-09-12",
                fecha_fin="2026-09-12",
                hora_inicio="08:30:00",
                hora_fin="17:00:00",
                is_synced=1,
                created_offline=0,
                updated_at=datetime.now(timezone.utc).isoformat()
            ),
            Actividad(
                id=str(uuid.uuid4()),
                codigo_actividad="ACT-2026-005",
                nombre="Taller práctico sobre arquitectura limpia",
                tipo_actividad_id=taller.id,
                unidad_responsable_id=fac_ing.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=auditorio_1.id,
                proposito="Taller práctico sobre arquitectura limpia y diseño estructural de vanguardia.",
                fecha_inicio="2026-09-25",
                fecha_fin="2026-09-25",
                hora_inicio="09:00:00",
                hora_fin="12:00:00",
                is_synced=1,
                created_offline=0,
                updated_at=datetime.now(timezone.utc).isoformat()
            ),
            # PASADOS
            Actividad(
                id=str(uuid.uuid4()),
                codigo_actividad="ACT-2026-006",
                nombre="Presentación final de trabajos de grado 2026-I",
                tipo_actividad_id=conferencia.id,
                unidad_responsable_id=fac_ing.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=auditorio_2.id,
                proposito="Presentación final de trabajos de grado de la cohorte 2026-I.",
                fecha_inicio="2026-07-10",
                fecha_fin="2026-07-10",
                hora_inicio="08:00:00",
                hora_fin="16:00:00",
                is_synced=1,
                created_offline=0,
                updated_at=datetime.now(timezone.utc).isoformat()
            ),
            Actividad(
                id=str(uuid.uuid4()),
                codigo_actividad="ACT-2026-007",
                nombre="Conferencia de telecomunicaciones y redes",
                tipo_actividad_id=conferencia.id,
                unidad_responsable_id=dactic.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=biblioteca.id,
                proposito="Conferencia de telecomunicaciones y redes de alta velocidad.",
                fecha_inicio="2026-06-02",
                fecha_fin="2026-06-02",
                hora_inicio="09:00:00",
                hora_fin="13:00:00",
                is_synced=1,
                created_offline=0,
                updated_at=datetime.now(timezone.utc).isoformat()
            ),
            Actividad(
                id=str(uuid.uuid4()),
                codigo_actividad="ACT-2026-008",
                nombre="Feria de proyectos comunitarios e innovación social",
                tipo_actividad_id=feria.id,
                unidad_responsable_id=dactic.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=auditorio_1.id,
                proposito="Feria de proyectos comunitarios e innovación social universitaria.",
                fecha_inicio="2026-05-18",
                fecha_fin="2026-05-18",
                hora_inicio="10:00:00",
                hora_fin="15:00:00",
                is_synced=1,
                created_offline=0,
                updated_at=datetime.now(timezone.utc).isoformat()
            )
        ]

        db.session.add_all(actividades_seed)
        db.session.commit()

        # ---------------------------------------------------------------------
        # 10. Asociar Lineamientos Estratégicos a Actividades de Demostración
        # ---------------------------------------------------------------------
        assoc_1 = ActividadLineamiento(
            id=str(uuid.uuid4()),
            actividad_id=actividades_seed[0].id,
            lineamiento_id=lineamiento_2_1.id,
            justificacion="Fomenta la exposición pública de investigaciones tecnológicas con aplicación al sector productivo."
        )
        assoc_2 = ActividadLineamiento(
            id=str(uuid.uuid4()),
            actividad_id=actividades_seed[0].id,
            lineamiento_id=lineamiento_3_1.id,
            justificacion="Incorpora proyectos basados en analítica de datos e inteligencia artificial."
        )
        assoc_3 = ActividadLineamiento(
            id=str(uuid.uuid4()),
            actividad_id=actividades_seed[2].id,
            lineamiento_id=lineamiento_3_1.id,
            justificacion="Discute la aplicación ética de modelos de inteligencia artificial en la ingeniería civil."
        )
        db.session.add_all([assoc_1, assoc_2, assoc_3])
        db.session.commit()

        # ---------------------------------------------------------------------
        # 11. Registrar Asistencias Iniciales
        # ---------------------------------------------------------------------
        asistencia_1 = Asistencia(
            id=str(uuid.uuid4()),
            actividad_id=actividades_seed[0].id,
            persona_id=p_est.id,
            usuario_registrador_id=user_encargado.id,
            timestamp_registro=datetime.now(timezone.utc).isoformat(),
            is_synced=1
        )
        asistencia_2 = Asistencia(
            id=str(uuid.uuid4()),
            actividad_id=actividades_seed[0].id,
            persona_id=p_trab.id,
            usuario_registrador_id=user_encargado.id,
            timestamp_registro=datetime.now(timezone.utc).isoformat(),
            is_synced=1
        )
        db.session.add_all([asistencia_1, asistencia_2])
        db.session.commit()

        print("[OK] Semilla de base de datos completada exitosamente:")
        print("   - Departamentos y Ciudades sembrados: 5 Departamentos / 7 Ciudades")
        print("   - Ejes y Lineamientos sembrados: 16 Ejes Oficiales de la Estrategia Nacional de Educación 2024-2026")
        print("   - Actividades creadas: 8 actividades (con marcado de lineamientos estratégicos)")
        print("   - Usuario Encargado: encargado@uni.edu.ni | Contraseña: admin123")
        print("   - Usuario Rector:    rector@uni.edu.ni    | Contraseña: rector123")

if __name__ == "__main__":
    seed_database()