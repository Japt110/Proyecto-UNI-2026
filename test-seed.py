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
        # Departamentos
        dep_boaco = Departamento(nombre="Boaco")
        dep_carazo = Departamento(nombre="Carazo")
        dep_chinandega = Departamento(nombre="Chinandega")
        dep_chontales = Departamento(nombre="Chontales")
        dep_esteli = Departamento(nombre="Estelí")
        dep_granada = Departamento(nombre="Granada")
        dep_jinotega = Departamento(nombre="Jinotega")
        dep_leon = Departamento(nombre="León")
        dep_madriz = Departamento(nombre="Madriz")
        dep_managua = Departamento(nombre="Managua")
        dep_masaya = Departamento(nombre="Masaya")
        dep_matalgalpa = Departamento(nombre="Matagalpa")
        dep_nueva_segovia = Departamento(nombre="Nueva Segovia")
        dep_rio_san_juan = Departamento(nombre="Río San Juan")
        dep_rivas = Departamento(nombre="Rivas")
        dep_costa_caribe_norte = Departamento(nombre="Costa Caribe Norte")
        dep_costa_caribe_sur = Departamento(nombre="Costa Caribe Sur")
        
        db.session.add_all([
            dep_boaco, dep_carazo, dep_chinandega, dep_chontales, dep_esteli,
            dep_granada, dep_jinotega, dep_leon, dep_madriz, dep_managua,
            dep_masaya, dep_matalgalpa, dep_nueva_segovia, dep_rio_san_juan,
            dep_rivas, dep_costa_caribe_norte, dep_costa_caribe_sur
        ])
        db.session.commit()
        print("[OK] Departamentos insertados")

        # Ciudades
        ciudades = [
            # Boaco (id: 1)
            Ciudad(nombre="Boaco", departamento_id=dep_boaco.id),
            Ciudad(nombre="Camoapa", departamento_id=dep_boaco.id),
            Ciudad(nombre="San José de los Remates", departamento_id=dep_boaco.id),
            Ciudad(nombre="San Lorenzo", departamento_id=dep_boaco.id),
            Ciudad(nombre="Santa Lucía", departamento_id=dep_boaco.id),
            Ciudad(nombre="Teustepe", departamento_id=dep_boaco.id),
            # Carazo (id: 2)
            Ciudad(nombre="Diriamba", departamento_id=dep_carazo.id),
            Ciudad(nombre="Dolores", departamento_id=dep_carazo.id),
            Ciudad(nombre="El Rosario", departamento_id=dep_carazo.id),
            Ciudad(nombre="Jinotepe", departamento_id=dep_carazo.id),
            Ciudad(nombre="La Conquista", departamento_id=dep_carazo.id),
            Ciudad(nombre="La Paz de Oriente", departamento_id=dep_carazo.id),
            Ciudad(nombre="San Marcos", departamento_id=dep_carazo.id),
            Ciudad(nombre="Santa Teresa", departamento_id=dep_carazo.id),
            # Chinandega (id: 3)
            Ciudad(nombre="Chichigalpa", departamento_id=dep_chinandega.id),
            Ciudad(nombre="Chinandega", departamento_id=dep_chinandega.id),
            Ciudad(nombre="Cinco Pinos", departamento_id=dep_chinandega.id),
            Ciudad(nombre="Corinto", departamento_id=dep_chinandega.id),
            Ciudad(nombre="El Realejo", departamento_id=dep_chinandega.id),
            Ciudad(nombre="El Viejo", departamento_id=dep_chinandega.id),
            Ciudad(nombre="Posoltega", departamento_id=dep_chinandega.id),
            Ciudad(nombre="Puerto Morazán", departamento_id=dep_chinandega.id),
            Ciudad(nombre="San Francisco del Norte", departamento_id=dep_chinandega.id),
            Ciudad(nombre="San Pedro del Norte", departamento_id=dep_chinandega.id),
            Ciudad(nombre="Santo Tomás del Norte", departamento_id=dep_chinandega.id),
            Ciudad(nombre="Somotillo", departamento_id=dep_chinandega.id),
            Ciudad(nombre="Villanueva", departamento_id=dep_chinandega.id),
            # Chontales (id: 4)
            Ciudad(nombre="Acoyapa", departamento_id=dep_chontales.id),
            Ciudad(nombre="Comalapa", departamento_id=dep_chontales.id),
            Ciudad(nombre="Cuapa", departamento_id=dep_chontales.id),
            Ciudad(nombre="El Coral", departamento_id=dep_chontales.id),
            Ciudad(nombre="Juigalpa", departamento_id=dep_chontales.id),
            Ciudad(nombre="La Libertad", departamento_id=dep_chontales.id),
            Ciudad(nombre="San Pedro de Lóvago", departamento_id=dep_chontales.id),
            Ciudad(nombre="Santo Domingo", departamento_id=dep_chontales.id),
            Ciudad(nombre="Santo Tomás", departamento_id=dep_chontales.id),
            Ciudad(nombre="Villa Sandino", departamento_id=dep_chontales.id),
            # Estelí (id: 5)
            Ciudad(nombre="Condega", departamento_id=dep_esteli.id),
            Ciudad(nombre="Estelí", departamento_id=dep_esteli.id),
            Ciudad(nombre="La Trinidad", departamento_id=dep_esteli.id),
            Ciudad(nombre="Pueblo Nuevo", departamento_id=dep_esteli.id),
            Ciudad(nombre="San Juan de Limay", departamento_id=dep_esteli.id),
            Ciudad(nombre="San Nicolás", departamento_id=dep_esteli.id),
            # Granada (id: 6)
            Ciudad(nombre="Diriá", departamento_id=dep_granada.id),
            Ciudad(nombre="Diriomo", departamento_id=dep_granada.id),
            Ciudad(nombre="Granada", departamento_id=dep_granada.id),
            Ciudad(nombre="Nandaime", departamento_id=dep_granada.id),
            # Jinotega (id: 7)
            Ciudad(nombre="El Cuá", departamento_id=dep_jinotega.id),
            Ciudad(nombre="Jinotega", departamento_id=dep_jinotega.id),
            Ciudad(nombre="La Concordia", departamento_id=dep_jinotega.id),
            Ciudad(nombre="San José de Bocay", departamento_id=dep_jinotega.id),
            Ciudad(nombre="San Rafael del Norte", departamento_id=dep_jinotega.id),
            Ciudad(nombre="San Sebastián de Yalí", departamento_id=dep_jinotega.id),
            Ciudad(nombre="Santa María de Pantasma", departamento_id=dep_jinotega.id),
            Ciudad(nombre="Wiwilí de Jinotega", departamento_id=dep_jinotega.id),
            # León (id: 8)
            Ciudad(nombre="Achuapa", departamento_id=dep_leon.id),
            Ciudad(nombre="El Jicaral", departamento_id=dep_leon.id),
            Ciudad(nombre="El Sauce", departamento_id=dep_leon.id),
            Ciudad(nombre="La Paz Centro", departamento_id=dep_leon.id),
            Ciudad(nombre="Larreynaga", departamento_id=dep_leon.id),
            Ciudad(nombre="León", departamento_id=dep_leon.id),
            Ciudad(nombre="Nagarote", departamento_id=dep_leon.id),
            Ciudad(nombre="Quezalguaque", departamento_id=dep_leon.id),
            Ciudad(nombre="Santa Rosa del Peñón", departamento_id=dep_leon.id),
            Ciudad(nombre="Telica", departamento_id=dep_leon.id),
            # Madriz (id: 9)
            Ciudad(nombre="Las Sabanas", departamento_id=dep_madriz.id),
            Ciudad(nombre="Palacagüina", departamento_id=dep_madriz.id),
            Ciudad(nombre="San José de Cusmapa", departamento_id=dep_madriz.id),
            Ciudad(nombre="San Juan de Río Coco", departamento_id=dep_madriz.id),
            Ciudad(nombre="San Lucas", departamento_id=dep_madriz.id),
            Ciudad(nombre="Somoto", departamento_id=dep_madriz.id),
            Ciudad(nombre="Telpaneca", departamento_id=dep_madriz.id),
            Ciudad(nombre="Totogalpa", departamento_id=dep_madriz.id),
            Ciudad(nombre="Yalagüina", departamento_id=dep_madriz.id),
            # Managua (id: 10)
            Ciudad(nombre="Ciudad Sandino", departamento_id=dep_managua.id),
            Ciudad(nombre="El Crucero", departamento_id=dep_managua.id),
            Ciudad(nombre="Managua", departamento_id=dep_managua.id),
            Ciudad(nombre="Mateare", departamento_id=dep_managua.id),
            Ciudad(nombre="San Francisco Libre", departamento_id=dep_managua.id),
            Ciudad(nombre="San Rafael del Sur", departamento_id=dep_managua.id),
            Ciudad(nombre="Ticuantepe", departamento_id=dep_managua.id),
            Ciudad(nombre="Tipitapa", departamento_id=dep_managua.id),
            Ciudad(nombre="Villa El Carmen", departamento_id=dep_managua.id),
            # Masaya (id: 11)
            Ciudad(nombre="Catarina", departamento_id=dep_masaya.id),
            Ciudad(nombre="La Concepción", departamento_id=dep_masaya.id),
            Ciudad(nombre="Masatepe", departamento_id=dep_masaya.id),
            Ciudad(nombre="Masaya", departamento_id=dep_masaya.id),
            Ciudad(nombre="Nandasmo", departamento_id=dep_masaya.id),
            Ciudad(nombre="Nindirí", departamento_id=dep_masaya.id),
            Ciudad(nombre="San Juan de Oriente", departamento_id=dep_masaya.id),
            Ciudad(nombre="Tisma", departamento_id=dep_masaya.id),
            # Matagalpa (id: 12)
            Ciudad(nombre="Ciudad Darío", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="El Tuma-La Dalia", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="Esquipulas", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="Matagalpa", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="Matiguás", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="Muy Muy", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="Rancho Grande", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="Río Blanco", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="San Dionisio", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="San Isidro", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="San Ramón", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="Sébaco", departamento_id=dep_matalgalpa.id),
            Ciudad(nombre="Terrabona", departamento_id=dep_matalgalpa.id),
            # Nueva Segovia (id: 13)
            Ciudad(nombre="Ciudad Antigua", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="Dipilto", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="El Jícaro", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="Jalapa", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="Macuelizo", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="Mosonte", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="Murra", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="Ocotal", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="Quilalí", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="San Fernando", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="Santa María", departamento_id=dep_nueva_segovia.id),
            Ciudad(nombre="Wiwilí de Nueva Segovia", departamento_id=dep_nueva_segovia.id),
            # Río San Juan (id: 14)
            Ciudad(nombre="El Almendro", departamento_id=dep_rio_san_juan.id),
            Ciudad(nombre="El Castillo", departamento_id=dep_rio_san_juan.id),
            Ciudad(nombre="Morrito", departamento_id=dep_rio_san_juan.id),
            Ciudad(nombre="San Carlos", departamento_id=dep_rio_san_juan.id),
            Ciudad(nombre="San Juan de Nicaragua", departamento_id=dep_rio_san_juan.id),
            Ciudad(nombre="San Miguelito", departamento_id=dep_rio_san_juan.id),
            # Rivas (id: 15)
            Ciudad(nombre="Altagracia", departamento_id=dep_rivas.id),
            Ciudad(nombre="Belén", departamento_id=dep_rivas.id),
            Ciudad(nombre="Buenos Aires", departamento_id=dep_rivas.id),
            Ciudad(nombre="Cárdenas", departamento_id=dep_rivas.id),
            Ciudad(nombre="Moyogalpa", departamento_id=dep_rivas.id),
            Ciudad(nombre="Potosí", departamento_id=dep_rivas.id),
            Ciudad(nombre="Rivas", departamento_id=dep_rivas.id),
            Ciudad(nombre="San Jorge", departamento_id=dep_rivas.id),
            Ciudad(nombre="San Juan del Sur", departamento_id=dep_rivas.id),
            Ciudad(nombre="Tola", departamento_id=dep_rivas.id),
            # Costa Caribe Norte (id: 16)
            Ciudad(nombre="Bonanza", departamento_id=dep_costa_caribe_norte.id),
            Ciudad(nombre="Mulukukú", departamento_id=dep_costa_caribe_norte.id),
            Ciudad(nombre="Prinzapolka", departamento_id=dep_costa_caribe_norte.id),
            Ciudad(nombre="Puerto Cabezas", departamento_id=dep_costa_caribe_norte.id),
            Ciudad(nombre="Rosita", departamento_id=dep_costa_caribe_norte.id),
            Ciudad(nombre="Siuna", departamento_id=dep_costa_caribe_norte.id),
            Ciudad(nombre="Waslala", departamento_id=dep_costa_caribe_norte.id),
            Ciudad(nombre="Waspán", departamento_id=dep_costa_caribe_norte.id),
            # Costa Caribe Sur (id: 17)
            Ciudad(nombre="Bluefields", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="Corn Island", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="Desembocadura de Río Grande", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="El Ayote", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="El Rama", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="El Tortuguero", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="Kukrahill", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="La Cruz de Río Grande", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="Muelle de los Bueyes", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="Nueva Guinea", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="Paiwas", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="Punta Gorda", departamento_id=dep_costa_caribe_sur.id),
            Ciudad(nombre="San Juan del Norte", departamento_id=dep_costa_caribe_sur.id),
        ]
        
        db.session.add_all(ciudades)
        db.session.commit()
        print("[OK] Ciudades insertadas")

        # ---------------------------------------------------------------------
        # 2. Insertar Sedes
        # ---------------------------------------------------------------------
        # Obtener ciudades de Managua y Juigalpa
        c_managua = Ciudad.query.filter_by(nombre="Managua", departamento_id=dep_managua.id).first()
        c_juigalpa = Ciudad.query.filter_by(nombre="Juigalpa", departamento_id=dep_chontales.id).first()
        c_esteli = Ciudad.query.filter_by(nombre="Estelí", departamento_id=dep_esteli.id).first()

        sede_rusb = Sede(nombre="Recinto Universitario Simón Bolívar", codigo="RUSB", ciudad_id=c_managua.id)
        sede_rupap = Sede(nombre="Recinto Universitario Pedro Aráuz Palacios", codigo="RUPAP", ciudad_id=c_managua.id)
        sede_ruacs = Sede(nombre="Recinto Universitario Augusto César Sandino", codigo="RUACS", ciudad_id=c_esteli.id)
        sede_rurc = Sede(nombre="Recinto Universitario Región Central", codigo="RURC", ciudad_id=c_juigalpa.id)

        db.session.add_all([sede_rusb, sede_rupap, sede_ruacs, sede_rurc])
        db.session.commit()
        print("[OK] Sedes insertadas")

        # ---------------------------------------------------------------------
        # 3. Insertar Espacios Físicos
        # ---------------------------------------------------------------------
        espacios = [
            EspacioFisico(sede_id=sede_rusb.id, nombre="Auditorio Salomón de la Selva", capacidad=50),
            EspacioFisico(sede_id=sede_rusb.id, nombre="Sala Rubén Darío", capacidad=50),
            EspacioFisico(sede_id=sede_rusb.id, nombre="Biblioteca", capacidad=50),
            EspacioFisico(sede_id=sede_rusb.id, nombre="Sala Blanca Arauz", capacidad=50),
            EspacioFisico(sede_id=sede_rupap.id, nombre="Sala Prokrainse", capacidad=50),
            EspacioFisico(sede_id=sede_rupap.id, nombre="Auditorio Areíto", capacidad=50),
            EspacioFisico(sede_id=sede_rupap.id, nombre="Biblioteca", capacidad=50),
            EspacioFisico(sede_id=sede_rupap.id, nombre="Auditorio Aldo Umbiva", capacidad=50),
        ]
        
        db.session.add_all(espacios)
        db.session.commit()
        print("[OK] Espacios físicos insertados")

        # ---------------------------------------------------------------------
        # 4. Insertar Unidades Organizativas
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
        print("[OK] Unidades organizativas insertadas")

        # ---------------------------------------------------------------------
        # 5. Insertar Tipos de Actividad
        # ---------------------------------------------------------------------
        tipos_actividad = [
            TipoActividad(nombre="Campaña", descripcion="Conjunto de acciones planificadas para promover una causa, difundir un mensaje o sensibilizar a la comunidad sobre un tema específico."),
            TipoActividad(nombre="Capacitación", descripcion="Proceso formativo orientado a desarrollar o fortalecer conocimientos, habilidades y competencias en un área específica."),
            TipoActividad(nombre="Charla", descripcion="Exposición oral sobre un tema determinado, generalmente de carácter informativo y con interacción con los participantes."),
            TipoActividad(nombre="Coloquio", descripcion="Reunión académica donde expertos discuten y debaten sobre un tema específico, con participación del público."),
            TipoActividad(nombre="Competencia", descripcion="Evento donde los participantes demuestran sus habilidades y conocimientos en un área específica, con un sistema de premiación."),
            TipoActividad(nombre="Conferencia", descripcion="Exposición magistral sobre un tema de interés, presentada por un especialista ante una audiencia."),
            TipoActividad(nombre="Congreso", descripcion="Reunión de especialistas donde se presentan y discuten trabajos de investigación y experiencias en un área del conocimiento."),
            TipoActividad(nombre="Conmemoración", descripcion="Actividad para recordar y celebrar fechas, eventos o personas significativas, con un enfoque histórico o cultural."),
            TipoActividad(nombre="Conversatorio", descripcion="Espacio de diálogo e intercambio de ideas entre participantes sobre un tema específico, con un enfoque participativo."),
            TipoActividad(nombre="Feria", descripcion="Evento que reúne expositores para mostrar y compartir productos, servicios, proyectos o experiencias en un ambiente dinámico."),
            TipoActividad(nombre="Festival", descripcion="Celebración que incluye diversas actividades artísticas, culturales, deportivas o recreativas, con un ambiente festivo."),
            TipoActividad(nombre="Foro", descripcion="Espacio de discusión y debate donde se abordan temas de interés general, con participación de especialistas y público."),
            TipoActividad(nombre="Jornada", descripcion="Encuentro que se desarrolla durante uno o varios días, con una agenda de actividades enfocadas en un tema específico."),
            TipoActividad(nombre="Reunión", descripcion="Encuentro entre personas para tratar asuntos específicos, coordinar acciones o tomar decisiones."),
            TipoActividad(nombre="Seminario", descripcion="Evento académico de carácter formativo donde se profundiza en un tema específico a través de ponencias y talleres."),
            TipoActividad(nombre="Simposio", descripcion="Reunión de especialistas donde se presentan y discuten ponencias sobre un tema específico, con un enfoque académico."),
            TipoActividad(nombre="Taller", descripcion="Espacio de aprendizaje práctico donde los participantes desarrollan habilidades a través de actividades guiadas."),
            TipoActividad(nombre="Torneo", descripcion="Competencia deportiva o académica donde los participantes compiten en diferentes etapas hasta definir un ganador."),
            TipoActividad(nombre="Zumbaton", descripcion="Evento de actividad física grupal, basado en ritmos latinos y música, que promueve la salud y el bienestar."),
            TipoActividad(nombre="Otro", descripcion="Categoría para actividades que no se ajustan a los tipos anteriores."),
        ]
        
        db.session.add_all(tipos_actividad)
        db.session.commit()
        print("[OK] Tipos de actividad insertados")

        # ---------------------------------------------------------------------
        # 6. Insertar Usuarios (con unidades organizativas)
        # ---------------------------------------------------------------------
        # Obtener la unidad TIC (asumo que dactic es TIC)
        dactic = UnidadOrganizativa.query.filter_by(codigo="TIC").first()
        
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
        print("[OK] Usuarios insertados")
        
                # ---------------------------------------------------------------------
        # 7. Insertar Ejes de Lineamiento
        # ---------------------------------------------------------------------
        ejes = [
            EjeLineamiento(
                numero_oficial="EJE 1",
                nombre="Educación para la Vida",
                descripcion="Promueve el aprendizaje continuo de capacidades, habilidades y valores para la formación integral como persona, para el trabajo y demás ámbitos de la vida."
            ),
            EjeLineamiento(
                numero_oficial="EJE 2",
                nombre="Educación en Valores",
                descripcion="Fomenta el conocimiento y práctica de valores fundamentales de las personas, familias y comunidades para el buen vivir y vivir con dignidad, basados en el amor a la vida, solidaridad, honestidad, responsabilidad, respeto, no violencia y cuido a nuestra madre tierra, entre otros."
            ),
            EjeLineamiento(
                numero_oficial="EJE 3",
                nombre="Educación Creativa",
                descripcion="Promueve la curiosidad desde la infancia, desarrollando habilidades y talentos para emprender acciones creativas e innovadoras en las distintas situaciones y ámbitos de la vida, para el desarrollo de las personas, familias y comunidades."
            ),
            EjeLineamiento(
                numero_oficial="EJE 4",
                nombre="Educación Artística y Cultural",
                descripcion="Contribuye al desarrollo de la formación integral para el disfrute y práctica de expresiones artísticas y culturales, que caracterizan nuestra identidad nacional."
            ),
            EjeLineamiento(
                numero_oficial="EJE 5",
                nombre="Historia e Identidad Nacional",
                descripcion="Fomenta el conocimiento, el aprendizaje y la apropiación de nuestra historia de lucha y la de pueblos hermanos, aportando sentido de pertenencia, identidad de nación, orgullo patrio para la defensa y protección de nuestro patrimonio histórico y cultural."
            ),
            EjeLineamiento(
                numero_oficial="EJE 6",
                nombre="Ambiente y Naturaleza",
                descripcion="Fortalece el desarrollo de conocimientos, valores y prácticas para la conservación, protección y cuido de nuestra Madre Tierra, aportando a la preservación de ambientes saludables para las futuras generaciones."
            ),
            EjeLineamiento(
                numero_oficial="EJE 7",
                nombre="Cambio Climático",
                descripcion="Desarrolla el pensamiento crítico y consciente ante la crisis climática de nuestro planeta, provocada principalmente por la acción humana, promoviendo prácticas de mitigación y adaptación a los efectos del cambio climático."
            ),
            EjeLineamiento(
                numero_oficial="EJE 8",
                nombre="Educación Física y Deportiva",
                descripcion="Fomenta la actividad física y deportiva, aportando al desarrollo integral de estudiantes, el cuido de la salud, la recreación sana y una vida libre de drogas y adicciones."
            ),
            EjeLineamiento(
                numero_oficial="EJE 9",
                nombre="Educación Especial Incluyente",
                descripcion="Promueve el desarrollo pleno e integral de niñ@s, adolescentes, jóvenes y adultos con discapacidad u otra condición, desarrollando su potencial para una mejor calidad de vida en igualdad de oportunidades."
            ),
            EjeLineamiento(
                numero_oficial="EJE 10",
                nombre="Ciencias",
                descripcion="Proporciona habilidades y destrezas para comprender y explicar fenómenos de la naturaleza, produciendo nuevos conocimientos orientados al desarrollo socio productivo del país."
            ),
            EjeLineamiento(
                numero_oficial="EJE 11",
                nombre="Investigación e Innovación",
                descripcion="La investigación promueve la aplicación de conocimientos, habilidades, métodos y medios para la generación de nuevos conocimientos y resultados en los ámbitos: educativo, económico y socio productivo del país. La innovación fomenta el aprovechamiento de los resultados de la investigación para la generación de propuestas que aporten al desarrollo humano y socio productivo del país."
            ),
            EjeLineamiento(
                numero_oficial="EJE 12",
                nombre="Cobertura Amplia, con Inclusión y Equidad Modalidad Presencial y Virtual",
                descripcion="Es la ampliación de oportunidades educativas en el campo y la ciudad, acercando la educación con calidad a las personas, familias y comunidades en todos los niveles y modalidades."
            ),
            EjeLineamiento(
                numero_oficial="EJE 13",
                nombre="Calidad Educativa",
                descripcion="Es la complementariedad de condiciones humanas y materiales para asegurar los aprendizajes con pertinencia y relevancia al desarrollo socio productivo de nuestro país, desde el derecho a la educación pública y gratuita en todos los niveles y modalidades educativas."
            ),
            EjeLineamiento(
                numero_oficial="EJE 14",
                nombre="Formación Docente",
                descripcion="Comprende el desarrollo de conocimientos pedagógicos y científicos, habilidades emocionales y de liderazgo, en fomento de su vocación de servicio para una educación de calidad. L@s maestr@s deben aprender y prepararse de forma continua para las nuevas realidades sociales y tecnológicas."
            ),
            EjeLineamiento(
                numero_oficial="EJE 15",
                nombre="Fortalecimiento Institucional",
                descripcion="Es la mejora continua de la gestión académica y administrativa, fortalecimiento de la vocación de servicio y compromiso de servidor@s públicos del sistema educativo, para atención con calidad a las personas, familias y comunidades."
            ),
            EjeLineamiento(
                numero_oficial="EJE 16",
                nombre="Infraestructura y Equipamiento",
                descripcion="Son las condiciones físicas, técnicas y tecnológicas que facilitan la calidad educativa desde la mejora continua de ambientes dignos e incluyentes, que favorecen los aprendizajes."
            ),
        ]
        
        db.session.add_all(ejes)
        db.session.commit()
        print("[OK] Ejes de lineamiento insertados")

        # ---------------------------------------------------------------------
        # 8. Insertar Lineamientos
        # ---------------------------------------------------------------------
        # Obtener referencias a los ejes
        eje1 = EjeLineamiento.query.filter_by(numero_oficial="EJE 1").first()
        eje2 = EjeLineamiento.query.filter_by(numero_oficial="EJE 2").first()
        eje3 = EjeLineamiento.query.filter_by(numero_oficial="EJE 3").first()
        eje4 = EjeLineamiento.query.filter_by(numero_oficial="EJE 4").first()
        eje5 = EjeLineamiento.query.filter_by(numero_oficial="EJE 5").first()
        eje6 = EjeLineamiento.query.filter_by(numero_oficial="EJE 6").first()
        eje7 = EjeLineamiento.query.filter_by(numero_oficial="EJE 7").first()
        eje8 = EjeLineamiento.query.filter_by(numero_oficial="EJE 8").first()
        eje9 = EjeLineamiento.query.filter_by(numero_oficial="EJE 9").first()
        eje10 = EjeLineamiento.query.filter_by(numero_oficial="EJE 10").first()
        eje11 = EjeLineamiento.query.filter_by(numero_oficial="EJE 11").first()
        eje12 = EjeLineamiento.query.filter_by(numero_oficial="EJE 12").first()
        eje13 = EjeLineamiento.query.filter_by(numero_oficial="EJE 13").first()
        eje14 = EjeLineamiento.query.filter_by(numero_oficial="EJE 14").first()
        eje15 = EjeLineamiento.query.filter_by(numero_oficial="EJE 15").first()
        eje16 = EjeLineamiento.query.filter_by(numero_oficial="EJE 16").first()

        lineamientos = [
            # Eje 1: Educación para la Vida
            Lineamiento(eje_id=eje1.id, numero_oficial="1.1", descripcion="Desarrollaremos la orientación vocacional y profesional de los estudiantes, desde la formación inicial hasta la educación técnica y universitaria."),
            Lineamiento(eje_id=eje1.id, numero_oficial="1.2", descripcion="Fortaleceremos la Vocación Productiva para el Trabajo y la Vida, con aprendizajes para la conservación de los recursos naturales y el desarrollo de prácticas productivas sostenibles, con estudiantes de secundaria a distancia en el campo."),
            Lineamiento(eje_id=eje1.id, numero_oficial="1.3", descripcion="Fomentaremos la continuidad educativa de jóvenes y adultos egresad@s de programas de alfabetización hacia las Escuelas Municipales de Oficios."),
            Lineamiento(eje_id=eje1.id, numero_oficial="1.4", descripcion="Promoveremos el protagonismo de la mujer en todos los niveles y modalidades educativas."),
            Lineamiento(eje_id=eje1.id, numero_oficial="1.5", descripcion="Promoveremos la integración y continuidad educativa de niñ@s, adolescentes, jóvenes y adultos que no han logrado integrarse a la educación: personas que viven en zonas rurales alejadas, privados de libertad, personas con horario laboral irregular, entre otros."),
            Lineamiento(eje_id=eje1.id, numero_oficial="1.6", descripcion="Promoveremos el hábito de lectura, escritura creativa y oratoria como herramientas para el crecimiento y bienestar personal en todas las modalidades educativas."),
            Lineamiento(eje_id=eje1.id, numero_oficial="1.7", descripcion="Promoveremos el pensamiento lógico - matemático y científico, como aprendizaje fundamental para la vida, en todas las modalidades educativas."),
            Lineamiento(eje_id=eje1.id, numero_oficial="1.8", descripcion="Fortaleceremos el aprendizaje del inglés como segundo idioma para estudiantes y docentes, en todos los niveles educativos, como herramienta para el desarrollo profesional y personal."),
            Lineamiento(eje_id=eje1.id, numero_oficial="1.9", descripcion="Promoveremos la práctica de hábitos saludables, para el bienestar individual, familiar y comunitario."),
            
            # Eje 2: Educación en Valores
            Lineamiento(eje_id=eje2.id, numero_oficial="2.1", descripcion="Promoveremos prácticas de valores, derechos y deberes para la convivencia de las personas, familias y comunidades desde los centros educativos, para una cultura de Paz y Bien."),
            Lineamiento(eje_id=eje2.id, numero_oficial="2.2", descripcion="Fortaleceremos la vocación de servicio de estudiantes técnicos y universitarios para el bien común."),
            Lineamiento(eje_id=eje2.id, numero_oficial="2.3", descripcion="Promoveremos el protagonismo de la familia y comunidad, para el apoyo y acompañamiento del proceso de aprendizaje."),
            
            # Eje 3: Educación Creativa
            Lineamiento(eje_id=eje3.id, numero_oficial="3.1", descripcion="Desarrollaremos la creatividad y la innovación que estimulen el pensamiento lógico en preescolar, primaria y secundaria."),
            Lineamiento(eje_id=eje3.id, numero_oficial="3.2", descripcion="Promoveremos iniciativas que proyecten habilidades, capacidades y destrezas de estudiantes y docentes para emprender acciones creativas e innovadoras."),
            
            # Eje 4: Educación Artística y Cultural
            Lineamiento(eje_id=eje4.id, numero_oficial="4.1", descripcion="Promoveremos las escuelas, centros técnicos y universidades como referentes para la práctica artística y cultural de la comunidad educativa."),
            Lineamiento(eje_id=eje4.id, numero_oficial="4.2", descripcion="Fortaleceremos las habilidades artísticas de los docentes de primaria y secundaria que imparten los Talleres de Arte y Cultura, a través de las Escuelas de Artes y Escuelas Municipales de Cultura y Creatividad."),
            Lineamiento(eje_id=eje4.id, numero_oficial="4.3", descripcion="Formaremos y certificaremos a maestros de las Escuelas Municipales de Arte, desde el Centro Cultural y Politécnico José Coronel Urtecho."),
            Lineamiento(eje_id=eje4.id, numero_oficial="4.4", descripcion="Promoveremos el valor de la cultura popular nicaragüense y el conocimiento ancestral, en todos los niveles educativos."),
            
            # Eje 5: Historia e Identidad Nacional
            Lineamiento(eje_id=eje5.id, numero_oficial="5.1", descripcion="Promoveremos el estudio de la Historia como asignatura fundamental, en la educación Primaria, Secundaria, Técnica y Universitaria."),
            Lineamiento(eje_id=eje5.id, numero_oficial="5.2", descripcion="Fomentaremos la investigación sobre la historia e identidad cultural."),
            Lineamiento(eje_id=eje5.id, numero_oficial="5.3", descripcion="Promoveremos espacios de diálogo y aprendizaje sobre la historia de lucha en Nicaragua."),
            
            # Eje 6: Ambiente y Naturaleza
            Lineamiento(eje_id=eje6.id, numero_oficial="6.1", descripcion="Promoveremos la formación y práctica ambiental para la concientización y adopción de compromisos por parte de la comunidad educativa."),
            Lineamiento(eje_id=eje6.id, numero_oficial="6.2", descripcion="Promoveremos el cuido y conservación del agua y el suelo, como recurso natural y fuente de vida."),
            Lineamiento(eje_id=eje6.id, numero_oficial="6.3", descripcion="Promoveremos el manejo responsable y aprovechamiento de la basura, con la comunidad educativa."),
            
            # Eje 7: Cambio Climático
            Lineamiento(eje_id=eje7.id, numero_oficial="7.1", descripcion="Promoveremos el desarrollo de conocimientos y saberes de las causas y consecuencias de la crisis climática, en todos los niveles educativos."),
            Lineamiento(eje_id=eje7.id, numero_oficial="7.2", descripcion="Promoveremos la investigación e innovación para la generación de propuestas de mitigación y adaptación a la crisis climática."),
            Lineamiento(eje_id=eje7.id, numero_oficial="7.3", descripcion="Fortaleceremos la sensibilización sobre la mitigación y adaptación al cambio climático."),
            
            # Eje 8: Educación Física y Deportiva
            Lineamiento(eje_id=eje8.id, numero_oficial="8.1", descripcion="Fomentaremos el deporte y la actividad física, para el desarrollo de talentos deportivos y una vida saludable."),
            Lineamiento(eje_id=eje8.id, numero_oficial="8.2", descripcion="Fortaleceremos las capacidades de los docentes primaria y secundaria para el desarrollo de la Educación Física."),
            Lineamiento(eje_id=eje8.id, numero_oficial="8.3", descripcion="Promoveremos el deporte de alto rendimiento con atletas universitarios y aportaremos a la mejora de su organización deportiva con la formación de instructores y realización de eventos."),
            
            # Eje 9: Educación Especial Incluyente
            Lineamiento(eje_id=eje9.id, numero_oficial="9.1", descripcion="Fortaleceremos la atención educativa a personas con discapacidad, en todos los niveles de la educación."),
            Lineamiento(eje_id=eje9.id, numero_oficial="9.2", descripcion="Fortaleceremos las capacidades de docentes para atención a estudiantes con discapacidad en todos los niveles y modalidades educativas."),
            Lineamiento(eje_id=eje9.id, numero_oficial="9.3", descripcion="Fortaleceremos las capacidades institucionales para la creación de material didáctico en atención a personas con discapacidad del Sistema Educativo Nacional."),
            
            # Eje 10: Ciencias
            Lineamiento(eje_id=eje10.id, numero_oficial="10.1", descripcion="Desarrollaremos el conocimiento de la ciencia y su relación con la vida, para la generación de nuevos conocimientos."),
            Lineamiento(eje_id=eje10.id, numero_oficial="10.2", descripcion="Promoveremos la ciencia en la comunidad, impulsando el intercambio de experiencias, conocimientos y saberes."),
            
            # Eje 11: Investigación e Innovación
            Lineamiento(eje_id=eje11.id, numero_oficial="11.1", descripcion="Fortaleceremos capacidades técnicas y metodológicas de estudiantes y docentes para la investigación, en todas las modalidades educativas."),
            Lineamiento(eje_id=eje11.id, numero_oficial="11.2", descripcion="Promoveremos la investigación científica y la innovación en estudiantes y docentes."),
            Lineamiento(eje_id=eje11.id, numero_oficial="11.3", descripcion="Desarrollaremos conocimientos y habilidades para la innovación pedagógica."),
            Lineamiento(eje_id=eje11.id, numero_oficial="11.4", descripcion="Promoveremos la investigación experimental en la educación técnica para la innovación, en aporte al desarrollo social y productivo del país."),
            Lineamiento(eje_id=eje11.id, numero_oficial="11.5", descripcion="Promoveremos la incubación de proyectos técnicos de estudiantes y docentes para la creación de modelos de negocios y protección de propiedad intelectual, desde la plataforma INNOVATEC."),
            Lineamiento(eje_id=eje11.id, numero_oficial="11.6", descripcion="Fortalecimiento del enlazamiento productivo con instituciones del Estado, Alcaldías y sectores socio productivos para la implementación y uso de aplicaciones generadas desde la plataforma Hackathon Nicaragua."),
            Lineamiento(eje_id=eje11.id, numero_oficial="11.7", descripcion="Incrementaremos la investigación científica en las universidades, incorporando las principales líneas de desarrollo del país."),
            Lineamiento(eje_id=eje11.id, numero_oficial="11.8", descripcion="Fomentaremos la innovación aportando soluciones creativas desde programas y plataformas como el Rally nacional y otras expresiones para el desarrollo socio productivo."),
            Lineamiento(eje_id=eje11.id, numero_oficial="11.9", descripcion="Promoveremos el resguardo de la propiedad intelectual de investigaciones e innovaciones."),
            Lineamiento(eje_id=eje11.id, numero_oficial="11.10", descripcion="Fomentaremos la transferencia científica y tecnológica desde los Centros de Innovación Abierta y Centros de Investigaciones Especializados."),
            
            # Eje 12: Cobertura Amplia, con Inclusión y Equidad Modalidad Presencial y Virtual
            Lineamiento(eje_id=eje12.id, numero_oficial="12.1", descripcion="Ampliaremos la educación preescolar en el campo, con modalidad flexible en zonas rurales dispersas."),
            Lineamiento(eje_id=eje12.id, numero_oficial="12.2", descripcion="Promoveremos la continuidad educativa de personas con discapacidad."),
            Lineamiento(eje_id=eje12.id, numero_oficial="12.3", descripcion="Promoveremos la especialización técnica a egresados de las Escuelas de Oficio elevando sus conocimientos y habilidades técnicas básicas a especializadas."),
            Lineamiento(eje_id=eje12.id, numero_oficial="12.4", descripcion="Crearemos Escuelas Técnicas de Campo Especializadas, en rubros y temáticas como: café, musáceas, ganado e inseminación, cadena de valor y comercialización de la producción agropecuaria, entre otros; en articulación con las instituciones del Sistema Nacional de Producción."),
            Lineamiento(eje_id=eje12.id, numero_oficial="12.5", descripcion="Fortaleceremos el Programa Universidad en el Campo (UNICAM) con oferta académica pertinente, contextualizada y de calidad para el desarrollo, bienestar y prosperidad de la familia y comunidad."),
            Lineamiento(eje_id=eje12.id, numero_oficial="12.6", descripcion="Ampliaremos la cobertura en carreras y cursos técnicos con la modalidad virtual y educación a distancia."),
            Lineamiento(eje_id=eje12.id, numero_oficial="12.7", descripcion="Fortaleceremos la Universidad Abierta en Línea (UALN) para el aseguramiento del acceso amplio a la educación superior."),
            
            # Eje 13: Calidad Educativa
            Lineamiento(eje_id=eje13.id, numero_oficial="13.1", descripcion="Educación en todas las modalidades, para propiciar aprendizajes significativos que impacten en el desarrollo humano pleno."),
            Lineamiento(eje_id=eje13.id, numero_oficial="13.2", descripcion="Implementaremos el nuevo sistema de evaluación para los aprendizajes en los diferentes niveles educativos, transitando hacia la evaluación formativa, orientada a construir aprendizajes significativos."),
            Lineamiento(eje_id=eje13.id, numero_oficial="13.3", descripcion="Fortaleceremos la educación intercultural bilingüe en la Costa Caribe, en todos los niveles y modalidades."),
            Lineamiento(eje_id=eje13.id, numero_oficial="13.4", descripcion="Fortaleceremos la especialización técnica y tecnológica en cursos y carreras, para rubros y sectores priorizados en el Plan Nacional de Lucha Contra la Pobreza."),
            Lineamiento(eje_id=eje13.id, numero_oficial="13.5", descripcion="Fortaleceremos la gestión educativa con el uso efectivo, ético y responsable de la inteligencia artificial y las tecnologías educativas."),
            Lineamiento(eje_id=eje13.id, numero_oficial="13.6", descripcion="Incentivaremos la producción y uso de herramientas digitales en los procesos de aprendizaje, para todos los niveles y modalidades."),
            Lineamiento(eje_id=eje13.id, numero_oficial="13.7", descripcion="Implementaremos el sistema de gestión de la calidad para la educación y capacitación técnica y tecnológica."),
            Lineamiento(eje_id=eje13.id, numero_oficial="13.8", descripcion="Promoveremos procesos permanentes para el aseguramiento de la calidad en la gestión académica y administrativa en las universidades."),
            
            # Eje 14: Formación Docente
            Lineamiento(eje_id=eje14.id, numero_oficial="14.1", descripcion="Consolidaremos la formación de nuevos docentes, para atención en todas las modalidades educativas."),
            Lineamiento(eje_id=eje14.id, numero_oficial="14.2", descripcion="Promoveremos la formación continua de docentes, en todas las modalidades educativas, para mejora de los procesos de aprendizajes."),
            Lineamiento(eje_id=eje14.id, numero_oficial="14.3", descripcion="Diseñaremos programas para formación y actualización de los docentes de la educación técnica en agregación de valor, investigación, innovación, tecnologías, entre otros."),
            Lineamiento(eje_id=eje14.id, numero_oficial="14.4", descripcion="Fortaleceremos la formación de docentes de la educación universitaria, en aporte a la mejora de la calidad educativa."),
            Lineamiento(eje_id=eje14.id, numero_oficial="14.5", descripcion="Promoveremos el talento y habilidades de docentes desde la convivencia y práctica del arte, cultura y deporte."),
            
            # Eje 15: Fortalecimiento Institucional
            Lineamiento(eje_id=eje15.id, numero_oficial="15.1", descripcion="Mejoraremos la efectividad y calidad de los servicios académicos y administrativos, mediante la transformación digital."),
            Lineamiento(eje_id=eje15.id, numero_oficial="15.2", descripcion="Desarrollaremos programas de formación continua a servidores académicos y administrativos, para la mejora de la gestión educativa."),
            Lineamiento(eje_id=eje15.id, numero_oficial="15.3", descripcion="Desarrollaremos el sistema de planificación de cursos y carreras técnicas y universitarias."),
            Lineamiento(eje_id=eje15.id, numero_oficial="15.4", descripcion="Fortaleceremos el intercambio de conocimientos y experiencias con instituciones educativas nacionales e internacionales."),
            Lineamiento(eje_id=eje15.id, numero_oficial="15.5", descripcion="Fortaleceremos los mecanismos de información y estadísticas para el mejoramiento continuo en la gestión académica y administrativa del Sistema Educativo Nacional."),
            Lineamiento(eje_id=eje15.id, numero_oficial="15.6", descripcion="Crearemos la Editorial \"Victorias Educativas\" para la producción de publicaciones y material educativo del Sistema Nacional de Educación."),
            
            # Eje 16: Infraestructura y Equipamiento
            Lineamiento(eje_id=eje16.id, numero_oficial="16.1", descripcion="Continuaremos con el programa de construcción y mejora de la infraestructura educativa en el campo y la ciudad."),
            Lineamiento(eje_id=eje16.id, numero_oficial="16.2", descripcion="Dotación de equipamiento didáctico, técnico y tecnológico para facilitar los aprendizajes de estudiantes de todas las modalidades educativas."),
        ]
        
        db.session.add_all(lineamientos)
        db.session.commit()
        print("[OK] Lineamientos insertados")

        # ---------------------------------------------------------------------
        # 9. Insertar Acciones Estratégicas
        # ---------------------------------------------------------------------
        acciones = [
            # Lineamiento 1.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.1").first().id,
                descripcion="Programa de orientación y formación vocacional, para educación inicial, primaria y secundaria, dirigido al autoconocimiento, información para la construcción de su vocación y toma de decisiones."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.1").first().id,
                descripcion="Programa de orientación y formación profesional, para estudiantes de educación técnica y universitaria, para la construcción de su proyecto de vida."
            ),
            # Lineamiento 1.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.2").first().id,
                descripcion="Programa de formación para la producción agropecuaria sostenible dirigida a estudiantes de secundaria en el campo para desarrollo comunitario de nuestros pueblos."
            ),
            # Lineamiento 1.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.3").first().id,
                descripcion="Programa de formación para el trabajo y la vida en las Escuelas Municipales de Oficios, dirigido a protagonistas de Alfabetización y Educación para Jóvenes y Adultos."
            ),
            # Lineamiento 1.4
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.4").first().id,
                descripcion="Plan de fortalecimiento para la permanencia y continuidad de la mujer en el sistema educativo, potenciando la práctica de valores, respeto y no violencia."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.4").first().id,
                descripcion="Programa de promoción del protagonismo de la mujer en las ciencias, matemáticas y tecnologías en todas las modalidades educativas."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.4").first().id,
                descripcion="Plan de fortalecimiento de la participación de mujeres, jóvenes y adultas, en cursos y carreras técnicas y universitarias de los sectores Agropecuario y Forestal, Industria y Construcción."
            ),
            # Lineamiento 1.5
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.5").first().id,
                descripcion="Adecuación de programas educativos para el ingreso y continuidad en el sistema educativo de personas que no han logrado integrarse a la educación en todas las modalidades."
            ),
            # Lineamiento 1.6
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.6").first().id,
                descripcion="Desarrollo de la comprensión lectora, expresión oral y escrita desde los procesos de aprendizaje a lo largo de la vida."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.6").first().id,
                descripcion="Programa de fomento a la lectura y escritura creativa, desde la escuela, centros tecnológicos, universidades, bibliotecas, con la integración de la familia y comunidad."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.6").first().id,
                descripcion="Programa de desarrollo de habilidades del lenguaje, comunicación y oratoria para el crecimiento y bienestar socioemocional en niñ@s, adolescentes, jóvenes y adultos."
            ),
            # Lineamiento 1.7
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.7").first().id,
                descripcion="Desarrollo del pensamiento lógico - matemático y científico desde los procesos de aprendizaje."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.7").first().id,
                descripcion="Plan de formación docente en metodologías activas para desarrollar el aprendizaje lógico matemático y científico."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.7").first().id,
                descripcion="Eventos académicos para la promoción del aprendizaje de las matemáticas, con el protagonismo de los estudiantes y docentes."
            ),
            # Lineamiento 1.8
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.8").first().id,
                descripcion="Incorporación del inglés como segundo idioma en planes de estudios de todas las modalidades educativas, para el desarrollo y certificación de habilidades lingüísticas con estándares internacionales."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.8").first().id,
                descripcion="Fortalecimiento de la formación de docentes del idioma inglés en didáctica lingüística, en correspondencia con estándares internacionales."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.8").first().id,
                descripcion="Programa de aprendizaje del idioma inglés dirigido a Servidores Públicos para fortalecimiento profesional y crecimiento personal."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.8").first().id,
                descripcion="Fortalecimiento del aprendizaje del idioma inglés con el uso de plataformas virtuales."
            ),
            # Lineamiento 1.9
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="1.9").first().id,
                descripcion="Programa integral de hábitos saludables: nutrición, actividad física, aprovechamiento de ambientes naturales, manejo de emociones para el bienestar individual, familiar y comunitario."
            ),
            # Lineamiento 2.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="2.1").first().id,
                descripcion="Plan de fortalecimiento de la convivencia y práctica de valores de solidaridad, respeto y reconocimiento de los derechos y deberes de las personas, familias y comunidades."
            ),
            # Lineamiento 2.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="2.2").first().id,
                descripcion="Programa de servicio a la comunidad \"compartiendo lo aprendido\", desde el voluntariado de estudiantes técnicos y universitarios."
            ),
            # Lineamiento 2.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="2.3").first().id,
                descripcion="Encuentros de intercambio familiar para afianzar valores, prevención de la violencia y el acompañamiento educativo de niñ@s, adolescentes y jóvenes, fortaleciendo el vínculo de la escuela y la familia."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="2.3").first().id,
                descripcion="Acompañamiento comunitario intercultural, con la presencia sistemática de las sabias y sabios en la interacción de los diálogos de saberes con la comunidad educativa de pueblos originarios y afrodescendientes."
            ),
            # Lineamiento 3.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="3.1").first().id,
                descripcion="Programa integral para el desarrollo de creatividad, innovación y emprendimiento en todas las áreas del conocimiento, con estudiantes del campo y la ciudad."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="3.1").first().id,
                descripcion="Festivales y ferias de creatividad e innovación para la presentación y proyección de ideas creativas y proyectos innovadores."
            ),
            # Lineamiento 3.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="3.2").first().id,
                descripcion="Plataforma de creatividad e innovación para el desarrollo de proyectos, con componentes: académicos, técnicos, tecnológicos, deportivos, artísticos y culturales."
            ),
            # Lineamiento 4.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="4.1").first().id,
                descripcion="Programa de promoción, disfrute y aprecio del arte y la cultura nicaragüense, orientado al desarrollo artístico y cultural, capacitaciones y diseño de recursos audiovisuales, con el protagonismo de la comunidad educativa."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="4.1").first().id,
                descripcion="Instalación de escuelas de referencia y aulas de experimentación artística, como espacios para desarrollo de la creatividad de estudiantes y prácticas de docentes."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="4.1").first().id,
                descripcion="Formación de promotores culturales y artísticos para la promoción de la creatividad y el arte, desde las escuelas, centros técnicos y universidades."
            ),
            # Lineamiento 4.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="4.2").first().id,
                descripcion="Programa de formación para los docentes de arte y cultura de primaria y secundaria, en las diferentes disciplinas artísticas, articulados con las Escuelas Municipales de Cultura y Creatividad."
            ),
            # Lineamiento 4.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="4.3").first().id,
                descripcion="Programa de formación y certificación de competencias artísticas a facilitadores y docentes de las Escuelas Municipales de Arte y Cultura, desde el Centro Cultural y Politécnico José Coronel Urtecho."
            ),
            # Lineamiento 4.4
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="4.4").first().id,
                descripcion="Eventos académicos y jornadas, desde el protagonismo de los estudiantes hacia la comunidad, que destaquen la cultura popular nicaragüense y conocimiento ancestral: efemérides, representaciones de hitos históricos y héroes nacionales, gastronomía, juegos tradicionales, danzas autóctonas, el Son Nica, el Huipil, trajes típicos, entre otros."
            ),
            # Lineamiento 5.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="5.1").first().id,
                descripcion="Fortalecimiento de planes de estudio, incorporando la historia en todas las modalidades educativas, afianzando nuestro patrimonio histórico y cultural; saberes y prácticas de nuestros pueblos."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="5.1").first().id,
                descripcion="Producción de materiales educativos, en formato físico, digital y Teleclases sobre la Historia e identidad nacional, dirigido a docentes y estudiantes."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="5.1").first().id,
                descripcion="Formación de docentes en metodologías activas y participativas para el aprendizaje de la historia."
            ),
            # Lineamiento 5.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="5.2").first().id,
                descripcion="Producción de investigaciones y publicaciones educativas sobre historia local y nacional: cultura, historia y saberes populares de las familias y comunidades; con estudiantes y docentes."
            ),
            # Lineamiento 5.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="5.3").first().id,
                descripcion="Eventos académicos para la apropiación de nuestra historia, resaltando los hitos de lucha por la soberanía nacional y autodeterminación, destacando el valor de nuestros próceres, héroes y heroínas nacionales, con especialistas nacionales, líderes comunitarios de nuestros pueblos y el protagonismo de estudiantes, docentes."
            ),
            # Lineamiento 6.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="6.1").first().id,
                descripcion="Centros educativos, centros tecnológicos y universidades como patrimonio ambiental de la comunidad, reconociendo a la Madre Tierra como dadora de vida para la pervivencia de nuestros pueblos, promoviendo la conservación, protección y cuido del ambiente y la naturaleza."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="6.1").first().id,
                descripcion="Actualización de planes y programas de estudios incorporando la educación ambiental en todas las modalidades educativas."
            ),
            # Lineamiento 6.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="6.2").first().id,
                descripcion="Programas de formación para el cuido y conservación del agua y suelo."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="6.2").first().id,
                descripcion="Jornadas dirigidas al cuido y conservación del agua y suelo como recursos naturales fuente de vida, con el protagonismo de estudiantes, docentes, familias y comunidades."
            ),
            # Lineamiento 6.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="6.3").first().id,
                descripcion="Formación en el manejo de basura y prácticas de reuso, reducción y reciclaje, para generar conciencia en el cuido y conservación de la Madre Tierra."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="6.3").first().id,
                descripcion="Jornadas interinstitucionales para el mantenimiento de ambientes educativos y comunitarios saludables."
            ),
            # Lineamiento 7.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="7.1").first().id,
                descripcion="Actualización de planes de estudio para el desarrollo del pensamiento crítico y consciente ante la crisis climática."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="7.1").first().id,
                descripcion="Programa de formación de prácticas de mitigación y adaptación a los efectos del cambio climático."
            ),
            # Lineamiento 7.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="7.2").first().id,
                descripcion="Proyectos de investigación e innovación para la adaptación y mitigación ante los efectos del cambio climático."
            ),
            # Lineamiento 7.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="7.3").first().id,
                descripcion="Campañas y jornadas de prevención, adaptación y mitigación frente al cambio climático, promoviendo la relación armoniosa de la comunidad educativa con la naturaleza."
            ),
            # Lineamiento 8.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="8.1").first().id,
                descripcion="Programa de promoción del deporte \"Vida saludable en Comunidad\", para el desarrollo de la actividad física, valores, habilidades deportivas y sana recreación de docentes y estudiantes en el campo y la ciudad."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="8.1").first().id,
                descripcion="Rescate de los juegos tradicionales de nuestros pueblos, para el disfrute y recreación sana de la comunidad educativa."
            ),
            # Lineamiento 8.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="8.2").first().id,
                descripcion="Programa de formación de docentes de Educación Física en estrategias de entrenamiento, nutrición y rendimiento deportivo."
            ),
            # Lineamiento 8.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="8.3").first().id,
                descripcion="Programa de formación de deportistas de alto rendimiento desde las universidades."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="8.3").first().id,
                descripcion="Programa de formación técnica para instructores y entrenadores deportivos."
            ),
            # Lineamiento 9.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="9.1").first().id,
                descripcion="Programa de formación en atención a personas con discapacidad, dirigido a personal académico y administrativo de las instituciones educativas."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="9.1").first().id,
                descripcion="Ferias, festivales, talleres y encuentros con las familias para fortalecer la integración y atención a personas con discapacidad en la comunidad educativa."
            ),
            # Lineamiento 9.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="9.2").first().id,
                descripcion="Programa de especialización docente para atención a estudiantes con discapacidad, en todos los niveles y modalidades educativas."
            ),
            # Lineamiento 9.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="9.3").first().id,
                descripcion="Producción de material educativo en formato interactivo (lenguaje de señas, audio descripción, pictogramas, sistema Braille u otros) para educación especial, en las diferentes modalidades."
            ),
            # Lineamiento 10.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="10.1").first().id,
                descripcion="Actualización de planes y programas de estudio para el aprendizaje de las ciencias básicas, promoviendo la observación, experimentación e investigación partiendo del entorno."
            ),
            # Lineamiento 10.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="10.2").first().id,
                descripcion="Espacios de intercambio que vinculen la ciencia con las escuelas, centros tecnológicos y universidades para compartir experiencias con profesionales de diversas especialidades que realizan ciencia."
            ),
            # Lineamiento 11.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.1").first().id,
                descripcion="Programa de formación y acompañamiento a docentes para el fortalecimiento de conocimientos y habilidades investigativas."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.1").first().id,
                descripcion="Metodologías didácticas que incentiven la observación, experimentación e investigación en las diferentes áreas del conocimiento, saberes y cosmovisión de nuestros pueblos, con estudiantes de todas las modalidades educativas."
            ),
            # Lineamiento 11.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.2").first().id,
                descripcion="Generación de nuevos conocimientos en los ámbitos: educativo, económico y socio productivo, de acuerdo con líneas de investigación del Sistema Educativo Nacional."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.2").first().id,
                descripcion="Plataformas para el desarrollo de proyectos de innovación que aporten soluciones creativas para el crecimiento socio productivo del país."
            ),
            # Lineamiento 11.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.3").first().id,
                descripcion="Plataforma de innovación pedagógica docente, para capacitación y desarrollo de proyectos, en aporte a la transformación educativa nacional."
            ),
            # Lineamiento 11.4
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.4").first().id,
                descripcion="Programa de investigación experimental en la Educación Técnica, para los procesos de innovación de la plataforma INNOVATEC."
            ),
            # Lineamiento 11.5
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.5").first().id,
                descripcion="Programa nacional de incubación de proyectos técnicos generados en la plataforma INNOVATEC."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.5").first().id,
                descripcion="Establecimiento de laboratorios de innovación en Centros Tecnológicos, para el desarrollo de la creatividad, investigación e innovación de estudiantes y docentes."
            ),
            # Lineamiento 11.6
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.6").first().id,
                descripcion="Programa de innovación social con modelos de negocio de base tecnológica generados desde la plataforma Hackathon Nicaragua."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.6").first().id,
                descripcion="Política de estímulo académico a estudiantes que propicien el desarrollo de proyectos de innovación social."
            ),
            # Lineamiento 11.7
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.7").first().id,
                descripcion="Agenda nacional de investigación, vinculada con instituciones del Estado, Alcaldías y sectores productivos."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.7").first().id,
                descripcion="Plataforma nacional para la presentación y proyección de resultados de profesionales dedicados a investigación, innovación y producción científica."
            ),
            # Lineamiento 11.8
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.8").first().id,
                descripcion="Festivales tecnológicos en promoción al emprendimiento científico, tecnológico y social."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.8").first().id,
                descripcion="Programas de formación que incorporen la investigación e innovación."
            ),
            # Lineamiento 11.9
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.9").first().id,
                descripcion="Plan de formación en propiedad intelectual con especial atención en derechos de autor y patentes."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.9").first().id,
                descripcion="Mecanismos de incentivo a la producción de patentes."
            ),
            # Lineamiento 11.10
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.10").first().id,
                descripcion="Programa de incubación de proyectos de innovación científica y tecnológica para la generación de propuestas de valor en aporte al desarrollo socioproductivo."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="11.10").first().id,
                descripcion="Programa de capacitación para la transferencia científica y tecnológica."
            ),
            # Lineamiento 12.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="12.1").first().id,
                descripcion="Adecuación de modalidades de atención en la formación preescolar para ampliación de cobertura y facilidad de acceso a las familias."
            ),
            # Lineamiento 12.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="12.2").first().id,
                descripcion="Programa de continuidad educativa de personas con discapacidad hacia los programas de formación técnica y universitaria."
            ),
            # Lineamiento 12.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="12.3").first().id,
                descripcion="Programa de especialización para egresados de las Escuelas Municipales de Oficio, en Centros Tecnológicos, para el escalamiento de la actividad económica familiar."
            ),
            # Lineamiento 12.4
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="12.4").first().id,
                descripcion="Programa de formación técnica especializada para egresados de las Escuelas Técnicas de Campo, aportando a la agricultura empresarial a pequeña y mediana escala."
            ),
            # Lineamiento 12.5
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="12.5").first().id,
                descripcion="Ampliación de cobertura de la Universidad en el Campo en todos los municipios y Regiones Autónomas."
            ),
            # Lineamiento 12.6
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="12.6").first().id,
                descripcion="Ampliación de la oferta formativa en modalidad virtual, en las ramas de comercio, tecnologías e idiomas."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="12.6").first().id,
                descripcion="Implementación de formación a distancia y formación dual para facilitar el acceso a los programas de formación técnica."
            ),
            # Lineamiento 12.7
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="12.7").first().id,
                descripcion="Ampliación de la oferta educativa universitaria en modalidad virtual."
            ),
            # Lineamiento 13.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.1").first().id,
                descripcion="Actualización de planes y programas de estudios principalmente en lectoescritura y comprensión lectora, matemáticas, idiomas, ciencias básicas, creatividad, innovación, tecnologías, historia e identidad nacional multiétnica, multicultural y multilingüe, incorporando temas trasversales como medio ambiente, cambio climático, gestión de riesgo, entre otros."
            ),
            # Lineamiento 13.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.2").first().id,
                descripcion="Programa de formación y acompañamiento a docentes para la evaluación formativa de los aprendizajes."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.2").first().id,
                descripcion="Sistema de pruebas nacionales para evaluación de los aprendizajes fundamentales, en niveles y modalidades del sistema educativo."
            ),
            # Lineamiento 13.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.3").first().id,
                descripcion="Planes de estudio y materiales didácticos con enfoque intercultural bilingüe y cosmovisiones de los pueblos multiétnicos."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.3").first().id,
                descripcion="Fortalecimiento de programas de alfabetización en lenguas maternas de los pueblos originarios y afrodescendientes."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.3").first().id,
                descripcion="Promover el aprendizaje de las lenguas maternas de los pueblos originarios y afrodescendientes en todas las modalidades educativas."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.3").first().id,
                descripcion="Desarrollo de la investigación sobre las lenguas como elemento fundamental en la pervivencia de la identidad y los sistemas de conocimientos, saberes y prácticas de los pueblos."
            ),
            # Lineamiento 13.4
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.4").first().id,
                descripcion="Oferta de cursos y carreras técnicas especializadas, para potenciar la productividad, agregación de valor y comercialización."
            ),
            # Lineamiento 13.5
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.5").first().id,
                descripcion="Incorporación de herramientas de inteligencia artificial en los procesos de aprendizaje y la gestión administrativa y académica."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.5").first().id,
                descripcion="Producción e implementación de tecnologías educativas en todas las modalidades."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.5").first().id,
                descripcion="Eventos de capacitación sobre el uso ético y responsable de la inteligencia artificial dirigidos a la comunidad educativa."
            ),
            # Lineamiento 13.6
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.6").first().id,
                descripcion="Programa de producción de aplicaciones y herramientas digitales para la educación, para complementar y facilitar los procesos de aprendizaje."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.6").first().id,
                descripcion="Integración del uso de tecnologías en los planes de estudio de todas las modalidades educativas."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.6").first().id,
                descripcion="Implementación de simuladores virtuales y realidad aumentada, generando experiencias de aprendizaje interactivas."
            ),
            # Lineamiento 13.7
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.7").first().id,
                descripcion="Consolidación de los sistemas de gestión de la calidad implementados en la educación y capacitación técnica, para la mejora continua de los procesos académicos y administrativos."
            ),
            # Lineamiento 13.8
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.8").first().id,
                descripcion="Desarrollo de los sistemas de gestión de la calidad en las universidades."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="13.8").first().id,
                descripcion="Procesos de acreditación institucional y de carreras a nivel nacional e internacional."
            ),
            # Lineamiento 14.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="14.1").first().id,
                descripcion="Actualización de planes y programas de formación de docentes en todas las modalidades, fortaleciendo conocimientos, saberes y habilidades pedagógicas, científicas, tecnológicas, lingüísticas y vocación de servicio, desde el modelo de educación incluyente, intercultural y con igualdad de género."
            ),
            # Lineamiento 14.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="14.2").first().id,
                descripcion="Programa para actualización pedagógica, científica y tecnológica de docentes."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="14.2").first().id,
                descripcion="Programa de especialización de docentes en metodologías para educación inicial, educación especial, educación en el campo y educación para adult@s, incluyente, intercultural y con igualdad de género."
            ),
            # Lineamiento 14.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="14.3").first().id,
                descripcion="Programa de formación y especialización de docentes en investigación, innovación, tecnologías y escalabilidad de procesos productivos."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="14.3").first().id,
                descripcion="Plataforma de Innovación Pedagógica de Docentes de la Educación Técnica, para diseño, producción y desarrollo de propuestas que aporten a la transformación educativa."
            ),
            # Lineamiento 14.4
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="14.4").first().id,
                descripcion="Programa de formación docente en áreas pedagógicas, científicas, de investigación e innovación."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="14.4").first().id,
                descripcion="Implementación del sistema nacional de categorización docente."
            ),
            # Lineamiento 14.5
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="14.5").first().id,
                descripcion="Programa de desarrollo del talento de docentes desde la convivencia educativa y práctica del arte, cultura y deporte, para aportar al desarrollo socioemocional."
            ),
            # Lineamiento 15.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.1").first().id,
                descripcion="Automatización de servicios académicos y administrativos para la atención con calidad a estudiantes, familias y comunidades."
            ),
            # Lineamiento 15.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.2").first().id,
                descripcion="Programa de capacitación dirigido a delegad@s, director@s de centros y asesor@s pedagógicos para fortalecer el desempeño de sus funciones y la atención con calidad y calidez a la comunidad educativa."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.2").first().id,
                descripcion="Programa de capacitación dirigido a servidores administrativos de instituciones educativas, para fortalecer el desempeño de sus funciones."
            ),
            # Lineamiento 15.3
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.3").first().id,
                descripcion="Mapeo de la oferta formativa del nivel técnico y universitario, como mecanismo para la identificación de brechas de formación de necesidades territoriales."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.3").first().id,
                descripcion="Creación de nuevas ofertas en cursos, carreras, posgrados y especialización técnica y profesional, orientados al desarrollo y necesidades socio productivas y científicas del país."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.3").first().id,
                descripcion="Continuidad educativa desde la complementariedad de carreras técnicas y universitarias."
            ),
            # Lineamiento 15.4
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.4").first().id,
                descripcion="Programa de intercambio con instituciones homólogas de países hermanos, para el fortalecimiento de la gestión educativa."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.4").first().id,
                descripcion="Programas de intercambio académico nacional e internacional para el desarrollo de investigaciones conjuntas, iniciativas de desarrollo interinstitucional, movilidad de docentes y estudiantes, entre otros."
            ),
            # Lineamiento 15.5
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.5").first().id,
                descripcion="Sistema nacional de estadísticas educativas, que facilite la toma de decisiones en el sistema educativo."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.5").first().id,
                descripcion="Sistema nacional de admisión y matrícula de las universidades."
            ),
            # Lineamiento 15.6
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="15.6").first().id,
                descripcion="Producción y reproducción de materiales y publicaciones del Sistema Educativo Nacional, fortaleciendo la producción educativa."
            ),
            # Lineamiento 16.1
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="16.1").first().id,
                descripcion="Plan de rehabilitación y mejora de la infraestructura educativa para la dignificación de los ambientes de aprendizaje."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="16.1").first().id,
                descripcion="Nuevos ambientes de aprendizaje para la formación integral de los estudiantes, en todas las modalidades educativas."
            ),
            # Lineamiento 16.2
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="16.2").first().id,
                descripcion="Plan de fortalecimiento y dotación de mobiliario para el desarrollo de la formación."
            ),
            AccionEstrategica(
                lineamiento_id=Lineamiento.query.filter_by(numero_oficial="16.2").first().id,
                descripcion="Dotación y mantenimiento de equipamiento técnico y tecnológico para el desarrollo de la formación y la gestión institucional."
            ),
        ]
        
        db.session.add_all(acciones)
        db.session.commit()
        print("[OK] Acciones estratégicas insertadas")

                # ---------------------------------------------------------------------
        # 10. Insertar Personas
        # ---------------------------------------------------------------------
        # Obtener referencias a ciudades y sedes
        ciudad_managua = Ciudad.query.filter_by(nombre="Managua", departamento_id=dep_managua.id).first()
        ciudad_esteli = Ciudad.query.filter_by(nombre="Estelí", departamento_id=dep_esteli.id).first()
        ciudad_juigalpa = Ciudad.query.filter_by(nombre="Juigalpa", departamento_id=dep_chontales.id).first()
        ciudad_tipitapa = Ciudad.query.filter_by(nombre="Tipitapa", departamento_id=dep_managua.id).first()
        ciudad_masaya = Ciudad.query.filter_by(nombre="Masaya", departamento_id=dep_masaya.id).first()
        ciudad_granada = Ciudad.query.filter_by(nombre="Granada", departamento_id=dep_granada.id).first()
        ciudad_matagalpa = Ciudad.query.filter_by(nombre="Matagalpa", departamento_id=dep_matalgalpa.id).first()
        ciudad_leon = Ciudad.query.filter_by(nombre="León", departamento_id=dep_leon.id).first()
        ciudad_rivas = Ciudad.query.filter_by(nombre="Rivas", departamento_id=dep_rivas.id).first()
        ciudad_san_carlos = Ciudad.query.filter_by(nombre="San Carlos", departamento_id=dep_rio_san_juan.id).first()
        ciudad_chinandega = Ciudad.query.filter_by(nombre="Chinandega", departamento_id=dep_chinandega.id).first()
        ciudad_condega = Ciudad.query.filter_by(nombre="Condega", departamento_id=dep_esteli.id).first()
        ciudad_la_trinidad = Ciudad.query.filter_by(nombre="La Trinidad", departamento_id=dep_esteli.id).first()
        ciudad_san_juan_limay = Ciudad.query.filter_by(nombre="San Juan de Limay", departamento_id=dep_esteli.id).first()
        ciudad_el_cua = Ciudad.query.filter_by(nombre="El Cuá", departamento_id=dep_jinotega.id).first()
        ciudad_santo_domingo = Ciudad.query.filter_by(nombre="Santo Domingo", departamento_id=dep_chontales.id).first()
        ciudad_villa_sandino = Ciudad.query.filter_by(nombre="Villa Sandino", departamento_id=dep_chontales.id).first()
        ciudad_acoyapa = Ciudad.query.filter_by(nombre="Acoyapa", departamento_id=dep_chontales.id).first()
        
        personas = [
            # Personas de la sede RUSB (Managua) - IDs 1-20
            Persona(
                numero_unico="A7B9C3D2",
                cedula="177-150593-0001A",
                nombres_apellidos="María José González Pérez",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="F8K2L5M9",
                cedula="177-220489-0002B",
                nombres_apellidos="Carlos Andrés Martínez López",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="R3T6Y8U1",
                cedula="177-300195-0003C",
                nombres_apellidos="Ana Lucía Ramírez Castro",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="P9Q2W7E4",
                cedula="177-050892-0004D",
                nombres_apellidos="Juan Manuel Morales Gómez",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="L5N8B3V7",
                cedula="177-171290-0005E",
                nombres_apellidos="Laura Elena Sánchez Rivera",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_masaya.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="X2C6F9H1",
                cedula="177-121296-0006F",
                nombres_apellidos="Pedro José Torres Reyes",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="M4K8J3P6",
                cedula="177-250388-0007G",
                nombres_apellidos="Diana Carolina Flores Mena",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_granada.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="Z9B5N2W8",
                cedula="177-191094-0008H",
                nombres_apellidos="Ricardo Andrés Castro Jiménez",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="T7R4E1Q9",
                cedula="177-081091-0009I",
                nombres_apellidos="Patricia Isabel Vega Solís",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_matagalpa.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="H3M6Y2U8",
                cedula="177-011093-0010J",
                nombres_apellidos="Fernando José Díaz Aguilar",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="Q5W9R7T2",
                cedula="177-151289-0011K",
                nombres_apellidos="Carmen Elena Herrera Sánchez",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_leon.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="Y1U4I8O3",
                cedula="177-030893-0012L",
                nombres_apellidos="José Luis Mendoza García",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="G8K2P5N7",
                cedula="177-270194-0013M",
                nombres_apellidos="Rosa María Chavarría López",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="D4F9H2J6",
                cedula="177-060696-0014N",
                nombres_apellidos="Mario Alberto Cruz Ortiz",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="B7V3C9W5",
                cedula="177-200191-0015O",
                nombres_apellidos="Lorena Beatriz Rojas Navarro",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="N2X6Y8Z4",
                cedula="177-141093-0016P",
                nombres_apellidos="Jorge Enrique Méndez Rivas",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_rivas.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="E9R3T6U1",
                cedula="177-290795-0017Q",
                nombres_apellidos="Sofía Alejandra Gutiérrez Morales",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="A5S7D2F1",
                cedula="177-160891-0018R",
                nombres_apellidos="Miguel Ángel Romero Castro",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="M8K4J6H3",
                cedula="177-070492-0019S",
                nombres_apellidos="Elena Cristina Calderón Zamora",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_san_carlos.id,
                sede_id=sede_rusb.id
            ),
            Persona(
                numero_unico="Z3X5C7V9",
                cedula="177-181095-0020T",
                nombres_apellidos="David Alejandro Páiz Rocha",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rusb.id
            ),
            # Personas de la sede RUPAP (Managua) - IDs 21-40
            Persona(
                numero_unico="B6N8M4K2",
                cedula="177-120394-0021U",
                nombres_apellidos="Karla Paola Vanegas Sandoval",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_chinandega.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="F7H3J9L1",
                cedula="177-081096-0022V",
                nombres_apellidos="Luis Fernando Blandón Espinoza",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="Q2W4E6R8",
                cedula="177-210590-0023W",
                nombres_apellidos="María Fernanda Zelaya Barrios",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="T5Y7U9I2",
                cedula="177-040692-0024X",
                nombres_apellidos="Francisco Javier Hurtado Cardenal",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="O4P6L9K3",
                cedula="177-300893-0025Y",
                nombres_apellidos="Gabriela Esther Pereira Calero",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_leon.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="C8V4B2N6",
                cedula="177-191191-0026Z",
                nombres_apellidos="Óscar Manuel Salgado Talavera",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="E1R7T3Y5",
                cedula="177-090893-0027A",
                nombres_apellidos="Natalia Isabel Baca Barrera",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="G9M2K5H7",
                cedula="177-260792-0028B",
                nombres_apellidos="Roberto Carlos Espinoza López",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_matagalpa.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="L3N6B8V2",
                cedula="177-110194-0029C",
                nombres_apellidos="Adriana Beatriz Solórzano Morales",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="P5R8T1W4",
                cedula="177-280391-0030D",
                nombres_apellidos="Manuel José González Hernández",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="J6K3M9N7",
                cedula="177-020289-0031E",
                nombres_apellidos="Cynthia Marcela Membreño Narváez",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="Z1X4C7V8",
                cedula="177-170891-0032F",
                nombres_apellidos="Edwin José Miranda Huete",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="H2F8D4S9",
                cedula="177-130395-0033G",
                nombres_apellidos="Paola Andrea Fletes Mendoza",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="W6Q9T3Y8",
                cedula="177-100490-0034H",
                nombres_apellidos="Héctor Antonio Cerda Rivera",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="R4U7I2O5",
                cedula="177-230991-0035I",
                nombres_apellidos="Mónica Lisseth Vivas Téllez",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_san_carlos.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="D9G5B3N1",
                cedula="177-011094-0036J",
                nombres_apellidos="Javier Esteban Ríos Martínez",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="M7K2P4S6",
                cedula="177-160388-0037K",
                nombres_apellidos="Silvia Elena Cuadra Fonseca",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="T8W3E6R1",
                cedula="177-211193-0038L",
                nombres_apellidos="César Augusto Fornos Cerda",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="Y5U2I7O4",
                cedula="177-250392-0039M",
                nombres_apellidos="Jackeline María Rocha Martínez",
                sexo="F",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_leon.id,
                sede_id=sede_rupap.id
            ),
            Persona(
                numero_unico="B9N6M3K8",
                cedula="177-141095-0040N",
                nombres_apellidos="Mauricio José Aráuz Quezada",
                sexo="M",
                ciudad_residencia_id=ciudad_managua.id,
                ciudad_procedencia_id=ciudad_managua.id,
                sede_id=sede_rupap.id
            ),
            # Personas de la sede RUACS (Estelí) - IDs 41-60
            Persona(
                numero_unico="X3Y7Q2K5",
                cedula="039-180292-0041O",
                nombres_apellidos="Martha Elena Reyes Castillo",
                sexo="F",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="A8D4F6H9",
                cedula="039-060393-0042P",
                nombres_apellidos="Wilmer José Lanuza Salgado",
                sexo="M",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_condega.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="N1M4K7B3",
                cedula="039-230691-0043Q",
                nombres_apellidos="Elizabeth Mabel Castellón Larios",
                sexo="F",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="G5R8T2Y9",
                cedula="039-110894-0044R",
                nombres_apellidos="Ronald Antonio Flores Zapata",
                sexo="M",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="P6W3E9Q8",
                cedula="039-290290-0045S",
                nombres_apellidos="Griselda María Jarquín Ortiz",
                sexo="F",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_la_trinidad.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="K2M7B5N9",
                cedula="039-160493-0046T",
                nombres_apellidos="Oscar René Medina Vásquez",
                sexo="M",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="U4I7O2R5",
                cedula="039-020392-0047U",
                nombres_apellidos="Xiomara Betsabé Mairena López",
                sexo="F",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="Z6X3C9V1",
                cedula="039-190491-0048V",
                nombres_apellidos="Gustavo Adolfo Laguna Altamirano",
                sexo="M",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_san_juan_limay.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="L9N4B6T7",
                cedula="039-270693-0049W",
                nombres_apellidos="Claudia Vanessa Urbina Cerna",
                sexo="F",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="W2F7R9E4",
                cedula="039-140295-0050X",
                nombres_apellidos="Erick Santiago Morales Tercero",
                sexo="M",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="J5Y8K3M1",
                cedula="039-030594-0051Y",
                nombres_apellidos="Claribel del Socorro Barberena Gutiérrez",
                sexo="F",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_el_cua.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="C7V4B2N8",
                cedula="039-280390-0052Z",
                nombres_apellidos="William Armando Reyes Rocha",
                sexo="M",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="R1T6Y9U3",
                cedula="039-120595-0053A",
                nombres_apellidos="Glenda Raquel Orozco Siles",
                sexo="F",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="H4K8J2M7",
                cedula="039-210994-0054B",
                nombres_apellidos="Marvin José Quevedo Manzanares",
                sexo="M",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="F9D5S7G2",
                cedula="039-050391-0055C",
                nombres_apellidos="Luz Marina Hernández Mercado",
                sexo="F",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_la_trinidad.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="T8Y3U6I9",
                cedula="039-260692-0056D",
                nombres_apellidos="Bryan Josué González Espinoza",
                sexo="M",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="M2N6B8V4",
                cedula="039-180694-0057E",
                nombres_apellidos="Katherine Paola Dávila Centeno",
                sexo="F",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="G7R4T2Y1",
                cedula="039-090190-0058F",
                nombres_apellidos="Jonathan Antonio García Rizo",
                sexo="M",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="Q3W8E6R4",
                cedula="039-130392-0059G",
                nombres_apellidos="María del Carmen Acevedo Pérez",
                sexo="F",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            Persona(
                numero_unico="X9C5V7B2",
                cedula="039-010793-0060H",
                nombres_apellidos="Emerson David Mejía Gonzales",
                sexo="M",
                ciudad_residencia_id=ciudad_esteli.id,
                ciudad_procedencia_id=ciudad_esteli.id,
                sede_id=sede_ruacs.id
            ),
            # Personas de la sede RURC (Juigalpa) - IDs 61-80
            Persona(
                numero_unico="K7N4M2B9",
                cedula="032-150593-0061I",
                nombres_apellidos="Lucía Monserrat Flores Calderón",
                sexo="F",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="S4D6F8H2",
                cedula="032-080495-0062J",
                nombres_apellidos="Francisco José Blandón Cárdenas",
                sexo="M",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="Y3U7I9O4",
                cedula="032-211295-0063K",
                nombres_apellidos="Ana Isabel Martínez Torrez",
                sexo="F",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_santo_domingo.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="N6M8K2P5",
                cedula="032-120190-0064L",
                nombres_apellidos="Rigoberto Antonio Oporta Gutiérrez",
                sexo="M",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="E2R4T6Y8",
                cedula="032-190893-0065M",
                nombres_apellidos="Mirna Elizabeth Torres Villanueva",
                sexo="F",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="V3C5X7Z9",
                cedula="032-060294-0066N",
                nombres_apellidos="Ismael Enrique Mercado Martínez",
                sexo="M",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_acoyapa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="L1K5N8B4",
                cedula="032-250492-0067O",
                nombres_apellidos="Johanna María Espinoza Peralta",
                sexo="F",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="Q6W9R3T7",
                cedula="032-030395-0068P",
                nombres_apellidos="Lester Ronaldo Cerda Hernández",
                sexo="M",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="Z4X7C9V2",
                cedula="032-170792-0069Q",
                nombres_apellidos="Laura Cristina Mendoza Rivas",
                sexo="F",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_villa_sandino.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="B3N6M8K1",
                cedula="032-140694-0070R",
                nombres_apellidos="Moisés David Blandón Espinoza",
                sexo="M",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="F7H3J9L5",
                cedula="032-280792-0071S",
                nombres_apellidos="Carla Vanessa Chavarría Jirón",
                sexo="F",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="G2R5T8Y1",
                cedula="032-090493-0072T",
                nombres_apellidos="Julio César Ramos Reyes",
                sexo="M",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="M6K9B4N2",
                cedula="032-160592-0073U",
                nombres_apellidos="María Elena Espinoza Gadea",
                sexo="F",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_santo_domingo.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="O7I3U5Y8",
                cedula="032-221293-0074V",
                nombres_apellidos="Henry Ismael Medrano Rojas",
                sexo="M",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="J4K8N2M6",
                cedula="032-080394-0075W",
                nombres_apellidos="Ruth Nohemí García Martínez",
                sexo="F",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="A9S6D3F8",
                cedula="032-010195-0076X",
                nombres_apellidos="Junior Enrique López Torrez",
                sexo="M",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_santo_domingo.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="B7V3C9W4",
                cedula="032-140293-0077Y",
                nombres_apellidos="Martha Cecilia Sotelo Calderón",
                sexo="F",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="D4F9H2J7",
                cedula="032-270692-0078Z",
                nombres_apellidos="Emilio José Orozco Marenco",
                sexo="M",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="P2R5T8Y3",
                cedula="032-190694-0079A",
                nombres_apellidos="Silvia Maribel Castro Ríos",
                sexo="F",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
            Persona(
                numero_unico="U3I7O2R9",
                cedula="032-060192-0080B",
                nombres_apellidos="Wilber Antonio Briones Vivas",
                sexo="M",
                ciudad_residencia_id=ciudad_juigalpa.id,
                ciudad_procedencia_id=ciudad_juigalpa.id,
                sede_id=sede_rurc.id
            ),
        ]
        
        db.session.add_all(personas)
        db.session.commit()
        print("[OK] Personas insertadas")

        # ---------------------------------------------------------------------
        # 11. Insertar Trabajadores
        # ---------------------------------------------------------------------
        # Obtener unidades organizativas
        unidad_rectoria = UnidadOrganizativa.query.filter_by(codigo="EDU").first()
        unidad_academica = UnidadOrganizativa.query.filter_by(codigo="ART").first()
        unidad_calidad = UnidadOrganizativa.query.filter_by(codigo="CSOC").first()
        
        # Mapear persona_id a objeto Persona
        personas_dict = {p.id: p for p in Persona.query.all()}
        
        trabajadores = [
            # Rectoría (unidad_id=1 = EDU)
            Trabajador(persona_id=1, codigo_trabajador="TRAB-0001", unidad_id=unidad_rectoria.id, cargo="Rector", condicion_laboral="Permanente"),
            Trabajador(persona_id=2, codigo_trabajador="TRAB-0002", unidad_id=unidad_rectoria.id, cargo="Vicerrector General", condicion_laboral="Permanente"),
            Trabajador(persona_id=3, codigo_trabajador="TRAB-0003", unidad_id=unidad_rectoria.id, cargo="Secretario General", condicion_laboral="Permanente"),
            Trabajador(persona_id=4, codigo_trabajador="TRAB-0004", unidad_id=unidad_rectoria.id, cargo="Asesor Legal", condicion_laboral="Permanente"),
            Trabajador(persona_id=5, codigo_trabajador="TRAB-0005", unidad_id=unidad_rectoria.id, cargo="Coordinador de Planificación", condicion_laboral="Permanente"),
            Trabajador(persona_id=6, codigo_trabajador="TRAB-0006", unidad_id=unidad_rectoria.id, cargo="Auditor Interno", condicion_laboral="Permanente"),
            Trabajador(persona_id=7, codigo_trabajador="TRAB-0007", unidad_id=unidad_rectoria.id, cargo="Asistente de Rectoría", condicion_laboral="Contratado"),
            Trabajador(persona_id=8, codigo_trabajador="TRAB-0008", unidad_id=unidad_rectoria.id, cargo="Coordinador de Comunicaciones", condicion_laboral="Permanente"),
            # Dirección Académica (unidad_id=2 = ART)
            Trabajador(persona_id=9, codigo_trabajador="TRAB-0009", unidad_id=unidad_academica.id, cargo="Director Académico", condicion_laboral="Permanente"),
            Trabajador(persona_id=10, codigo_trabajador="TRAB-0010", unidad_id=unidad_academica.id, cargo="Subdirector Académico", condicion_laboral="Permanente"),
            Trabajador(persona_id=11, codigo_trabajador="TRAB-0011", unidad_id=unidad_academica.id, cargo="Coordinador de Carreras", condicion_laboral="Permanente"),
            Trabajador(persona_id=12, codigo_trabajador="TRAB-0012", unidad_id=unidad_academica.id, cargo="Coordinador de Currículo", condicion_laboral="Permanente"),
            Trabajador(persona_id=13, codigo_trabajador="TRAB-0013", unidad_id=unidad_academica.id, cargo="Coordinador de Evaluación", condicion_laboral="Permanente"),
            Trabajador(persona_id=14, codigo_trabajador="TRAB-0014", unidad_id=unidad_academica.id, cargo="Coordinador de Prácticas Profesionales", condicion_laboral="Contratado"),
            Trabajador(persona_id=15, codigo_trabajador="TRAB-0015", unidad_id=unidad_academica.id, cargo="Asistente Académico", condicion_laboral="Contratado"),
            Trabajador(persona_id=16, codigo_trabajador="TRAB-0016", unidad_id=unidad_academica.id, cargo="Secretaria Académica", condicion_laboral="Permanente"),
            Trabajador(persona_id=17, codigo_trabajador="TRAB-0017", unidad_id=unidad_academica.id, cargo="Coordinador de Horarios", condicion_laboral="Contratado"),
            Trabajador(persona_id=18, codigo_trabajador="TRAB-0018", unidad_id=unidad_academica.id, cargo="Analista de Datos Académicos", condicion_laboral="Permanente"),
            Trabajador(persona_id=19, codigo_trabajador="TRAB-0019", unidad_id=unidad_academica.id, cargo="Asistente de Subdirección", condicion_laboral="Contratado"),
            Trabajador(persona_id=20, codigo_trabajador="TRAB-0020", unidad_id=unidad_academica.id, cargo="Coordinador de Proyectos Académicos", condicion_laboral="Contratado"),
            Trabajador(persona_id=21, codigo_trabajador="TRAB-0021", unidad_id=unidad_academica.id, cargo="Coordinador de Acreditación", condicion_laboral="Permanente"),
            Trabajador(persona_id=22, codigo_trabajador="TRAB-0022", unidad_id=unidad_academica.id, cargo="Asistente de Coordinación", condicion_laboral="Contratado"),
            # Dirección de Calidad (unidad_id=3 = CSOC)
            Trabajador(persona_id=23, codigo_trabajador="TRAB-0023", unidad_id=unidad_calidad.id, cargo="Director de Calidad", condicion_laboral="Permanente"),
            Trabajador(persona_id=24, codigo_trabajador="TRAB-0024", unidad_id=unidad_calidad.id, cargo="Subdirector de Calidad", condicion_laboral="Permanente"),
            Trabajador(persona_id=25, codigo_trabajador="TRAB-0025", unidad_id=unidad_calidad.id, cargo="Coordinador de Procesos", condicion_laboral="Permanente"),
            Trabajador(persona_id=26, codigo_trabajador="TRAB-0026", unidad_id=unidad_calidad.id, cargo="Coordinador de Evaluación Interna", condicion_laboral="Permanente"),
            Trabajador(persona_id=27, codigo_trabajador="TRAB-0027", unidad_id=unidad_calidad.id, cargo="Coordinador de Mejora Continua", condicion_laboral="Permanente"),
            Trabajador(persona_id=28, codigo_trabajador="TRAB-0028", unidad_id=unidad_calidad.id, cargo="Coordinador de Auditorías", condicion_laboral="Contratado"),
            Trabajador(persona_id=29, codigo_trabajador="TRAB-0029", unidad_id=unidad_calidad.id, cargo="Analista de Calidad", condicion_laboral="Permanente"),
            Trabajador(persona_id=30, codigo_trabajador="TRAB-0030", unidad_id=unidad_calidad.id, cargo="Asistente de Calidad", condicion_laboral="Contratado"),
            Trabajador(persona_id=31, codigo_trabajador="TRAB-0031", unidad_id=unidad_calidad.id, cargo="Coordinador de Indicadores", condicion_laboral="Permanente"),
            Trabajador(persona_id=32, codigo_trabajador="TRAB-0032", unidad_id=unidad_calidad.id, cargo="Secretaria de Calidad", condicion_laboral="Permanente"),
            Trabajador(persona_id=33, codigo_trabajador="TRAB-0033", unidad_id=unidad_calidad.id, cargo="Asistente de Procesos", condicion_laboral="Contratado"),
            Trabajador(persona_id=34, codigo_trabajador="TRAB-0034", unidad_id=unidad_calidad.id, cargo="Coordinador de Documentación", condicion_laboral="Contratado"),
            Trabajador(persona_id=35, codigo_trabajador="TRAB-0035", unidad_id=unidad_calidad.id, cargo="Analista de Riesgos", condicion_laboral="Permanente"),
            Trabajador(persona_id=36, codigo_trabajador="TRAB-0036", unidad_id=unidad_calidad.id, cargo="Coordinador de Proyectos de Calidad", condicion_laboral="Contratado"),
            Trabajador(persona_id=37, codigo_trabajador="TRAB-0037", unidad_id=unidad_calidad.id, cargo="Asistente de Mejora Continua", condicion_laboral="Contratado"),
            Trabajador(persona_id=38, codigo_trabajador="TRAB-0038", unidad_id=unidad_calidad.id, cargo="Coordinador de Capacitación", condicion_laboral="Permanente"),
            Trabajador(persona_id=39, codigo_trabajador="TRAB-0039", unidad_id=unidad_calidad.id, cargo="Asistente de Auditorías", condicion_laboral="Contratado"),
            Trabajador(persona_id=40, codigo_trabajador="TRAB-0040", unidad_id=unidad_calidad.id, cargo="Analista de Acreditación", condicion_laboral="Permanente"),
        ]
        
        db.session.add_all(trabajadores)
        db.session.commit()
        print("[OK] Trabajadores insertados")

        # ---------------------------------------------------------------------
        # 12. Insertar Estudiantes
        # ---------------------------------------------------------------------
        # Obtener área de conocimiento (asumo que es TIC)
        area_conocimiento = UnidadOrganizativa.query.filter_by(codigo="TIC").first()
        
        estudiantes = [
            # Estudiantes de la sede RUSB (IDs 1-20)
            Estudiante(persona_id=1, carnet_estudiante="2022-123I", area_conocimiento_id=area_conocimiento.id, carrera="Computación", ano_academico=3, grupo="3M1-COM", turno="Matutino"),
            Estudiante(persona_id=2, carnet_estudiante="2021-456U", area_conocimiento_id=area_conocimiento.id, carrera="Sistemas", ano_academico=4, grupo="4M1-SIS", turno="Matutino"),
            Estudiante(persona_id=3, carnet_estudiante="2023-789I", area_conocimiento_id=area_conocimiento.id, carrera="Civil", ano_academico=2, grupo="2M1-CIV", turno="Matutino"),
            Estudiante(persona_id=4, carnet_estudiante="2020-234U", area_conocimiento_id=area_conocimiento.id, carrera="Electrónica", ano_academico=5, grupo="5T1-ELE", turno="Vespertino"),
            Estudiante(persona_id=5, carnet_estudiante="2022-567I", area_conocimiento_id=area_conocimiento.id, carrera="Industrial", ano_academico=3, grupo="3T1-IND", turno="Vespertino"),
            Estudiante(persona_id=6, carnet_estudiante="2021-890U", area_conocimiento_id=area_conocimiento.id, carrera="Química", ano_academico=4, grupo="4S1-QUI", turno="Sabatino"),
            Estudiante(persona_id=7, carnet_estudiante="2023-123U", area_conocimiento_id=area_conocimiento.id, carrera="Arquitectura", ano_academico=2, grupo="2M1-ARQ", turno="Matutino"),
            Estudiante(persona_id=8, carnet_estudiante="2020-456I", area_conocimiento_id=area_conocimiento.id, carrera="Sistemas", ano_academico=5, grupo="5M1-SIS", turno="Matutino"),
            Estudiante(persona_id=9, carnet_estudiante="2022-789U", area_conocimiento_id=area_conocimiento.id, carrera="Computación", ano_academico=3, grupo="3T2-COM", turno="Vespertino"),
            Estudiante(persona_id=10, carnet_estudiante="2021-012I", area_conocimiento_id=area_conocimiento.id, carrera="Civil", ano_academico=4, grupo="4M2-CIV", turno="Matutino"),
            Estudiante(persona_id=11, carnet_estudiante="2023-345U", area_conocimiento_id=area_conocimiento.id, carrera="Electrónica", ano_academico=2, grupo="2T1-ELE", turno="Vespertino"),
            Estudiante(persona_id=12, carnet_estudiante="2020-678I", area_conocimiento_id=area_conocimiento.id, carrera="Industrial", ano_academico=5, grupo="5S1-IND", turno="Sabatino"),
            Estudiante(persona_id=13, carnet_estudiante="2022-901U", area_conocimiento_id=area_conocimiento.id, carrera="Química", ano_academico=3, grupo="3M2-QUI", turno="Matutino"),
            Estudiante(persona_id=14, carnet_estudiante="2021-234I", area_conocimiento_id=area_conocimiento.id, carrera="Arquitectura", ano_academico=4, grupo="4T1-ARQ", turno="Vespertino"),
            Estudiante(persona_id=15, carnet_estudiante="2023-567U", area_conocimiento_id=area_conocimiento.id, carrera="Sistemas", ano_academico=2, grupo="2S1-SIS", turno="Sabatino"),
            Estudiante(persona_id=16, carnet_estudiante="2020-890I", area_conocimiento_id=area_conocimiento.id, carrera="Computación", ano_academico=5, grupo="5M2-COM", turno="Matutino"),
            Estudiante(persona_id=17, carnet_estudiante="2022-123U", area_conocimiento_id=area_conocimiento.id, carrera="Civil", ano_academico=3, grupo="3T3-CIV", turno="Vespertino"),
            Estudiante(persona_id=18, carnet_estudiante="2021-456I", area_conocimiento_id=area_conocimiento.id, carrera="Electrónica", ano_academico=4, grupo="4M3-ELE", turno="Matutino"),
            Estudiante(persona_id=19, carnet_estudiante="2023-789U", area_conocimiento_id=area_conocimiento.id, carrera="Industrial", ano_academico=2, grupo="2M2-IND", turno="Matutino"),
            Estudiante(persona_id=20, carnet_estudiante="2020-012I", area_conocimiento_id=area_conocimiento.id, carrera="Química", ano_academico=6, grupo="6S1-QUI", turno="Sabatino"),
            # Estudiantes de la sede RUPAP (IDs 21-40)
            Estudiante(persona_id=21, carnet_estudiante="2021-345U", area_conocimiento_id=area_conocimiento.id, carrera="Arquitectura", ano_academico=4, grupo="4T2-ARQ", turno="Vespertino"),
            Estudiante(persona_id=22, carnet_estudiante="2023-678I", area_conocimiento_id=area_conocimiento.id, carrera="Sistemas", ano_academico=2, grupo="2M3-SIS", turno="Matutino"),
            Estudiante(persona_id=23, carnet_estudiante="2020-901U", area_conocimiento_id=area_conocimiento.id, carrera="Computación", ano_academico=5, grupo="5S2-COM", turno="Sabatino"),
            Estudiante(persona_id=24, carnet_estudiante="2022-234I", area_conocimiento_id=area_conocimiento.id, carrera="Civil", ano_academico=3, grupo="3M4-CIV", turno="Matutino"),
            Estudiante(persona_id=25, carnet_estudiante="2021-567U", area_conocimiento_id=area_conocimiento.id, carrera="Electrónica", ano_academico=4, grupo="4T3-ELE", turno="Vespertino"),
            Estudiante(persona_id=26, carnet_estudiante="2023-890I", area_conocimiento_id=area_conocimiento.id, carrera="Industrial", ano_academico=2, grupo="2S2-IND", turno="Sabatino"),
            Estudiante(persona_id=27, carnet_estudiante="2020-123U", area_conocimiento_id=area_conocimiento.id, carrera="Química", ano_academico=6, grupo="6M1-QUI", turno="Matutino"),
            Estudiante(persona_id=28, carnet_estudiante="2022-456I", area_conocimiento_id=area_conocimiento.id, carrera="Arquitectura", ano_academico=3, grupo="3T4-ARQ", turno="Vespertino"),
            Estudiante(persona_id=29, carnet_estudiante="2021-789U", area_conocimiento_id=area_conocimiento.id, carrera="Sistemas", ano_academico=4, grupo="4S2-SIS", turno="Sabatino"),
            Estudiante(persona_id=30, carnet_estudiante="2023-012I", area_conocimiento_id=area_conocimiento.id, carrera="Computación", ano_academico=2, grupo="2M4-COM", turno="Matutino"),
            Estudiante(persona_id=31, carnet_estudiante="2020-345U", area_conocimiento_id=area_conocimiento.id, carrera="Civil", ano_academico=5, grupo="5T2-CIV", turno="Vespertino"),
            Estudiante(persona_id=32, carnet_estudiante="2022-678I", area_conocimiento_id=area_conocimiento.id, carrera="Electrónica", ano_academico=3, grupo="3M5-ELE", turno="Matutino"),
            Estudiante(persona_id=33, carnet_estudiante="2021-901U", area_conocimiento_id=area_conocimiento.id, carrera="Industrial", ano_academico=4, grupo="4S3-IND", turno="Sabatino"),
            Estudiante(persona_id=34, carnet_estudiante="2023-234I", area_conocimiento_id=area_conocimiento.id, carrera="Química", ano_academico=2, grupo="2T2-QUI", turno="Vespertino"),
            Estudiante(persona_id=35, carnet_estudiante="2020-567U", area_conocimiento_id=area_conocimiento.id, carrera="Arquitectura", ano_academico=5, grupo="5M3-ARQ", turno="Matutino"),
            Estudiante(persona_id=36, carnet_estudiante="2022-890I", area_conocimiento_id=area_conocimiento.id, carrera="Sistemas", ano_academico=3, grupo="3S3-SIS", turno="Sabatino"),
            Estudiante(persona_id=37, carnet_estudiante="2021-123U", area_conocimiento_id=area_conocimiento.id, carrera="Computación", ano_academico=4, grupo="4T4-COM", turno="Vespertino"),
            Estudiante(persona_id=38, carnet_estudiante="2023-456I", area_conocimiento_id=area_conocimiento.id, carrera="Civil", ano_academico=2, grupo="2M5-CIV", turno="Matutino"),
            Estudiante(persona_id=39, carnet_estudiante="2020-789U", area_conocimiento_id=area_conocimiento.id, carrera="Electrónica", ano_academico=6, grupo="6T1-ELE", turno="Vespertino"),
            Estudiante(persona_id=40, carnet_estudiante="2022-012I", area_conocimiento_id=area_conocimiento.id, carrera="Industrial", ano_academico=3, grupo="3S4-IND", turno="Sabatino"),
            # Estudiantes de la sede RUACS (IDs 41-60)
            Estudiante(persona_id=41, carnet_estudiante="2021-345I", area_conocimiento_id=area_conocimiento.id, carrera="Computación", ano_academico=4, grupo="4M6-COM", turno="Matutino"),
            Estudiante(persona_id=42, carnet_estudiante="2023-678U", area_conocimiento_id=area_conocimiento.id, carrera="Sistemas", ano_academico=2, grupo="2T3-SIS", turno="Vespertino"),
            Estudiante(persona_id=43, carnet_estudiante="2020-901I", area_conocimiento_id=area_conocimiento.id, carrera="Civil", ano_academico=5, grupo="5S4-CIV", turno="Sabatino"),
            Estudiante(persona_id=44, carnet_estudiante="2022-234U", area_conocimiento_id=area_conocimiento.id, carrera="Electrónica", ano_academico=3, grupo="3M7-ELE", turno="Matutino"),
            Estudiante(persona_id=45, carnet_estudiante="2021-567I", area_conocimiento_id=area_conocimiento.id, carrera="Industrial", ano_academico=4, grupo="4T5-IND", turno="Vespertino"),
            Estudiante(persona_id=46, carnet_estudiante="2023-890U", area_conocimiento_id=area_conocimiento.id, carrera="Química", ano_academico=2, grupo="2S3-QUI", turno="Sabatino"),
            Estudiante(persona_id=47, carnet_estudiante="2020-123I", area_conocimiento_id=area_conocimiento.id, carrera="Arquitectura", ano_academico=5, grupo="5M4-ARQ", turno="Matutino"),
            Estudiante(persona_id=48, carnet_estudiante="2022-456U", area_conocimiento_id=area_conocimiento.id, carrera="Sistemas", ano_academico=3, grupo="3T6-SIS", turno="Vespertino"),
            Estudiante(persona_id=49, carnet_estudiante="2021-789I", area_conocimiento_id=area_conocimiento.id, carrera="Computación", ano_academico=4, grupo="4S5-COM", turno="Sabatino"),
            Estudiante(persona_id=50, carnet_estudiante="2023-012U", area_conocimiento_id=area_conocimiento.id, carrera="Civil", ano_academico=2, grupo="2M6-CIV", turno="Matutino"),
            Estudiante(persona_id=51, carnet_estudiante="2020-345I", area_conocimiento_id=area_conocimiento.id, carrera="Electrónica", ano_academico=6, grupo="6T2-ELE", turno="Vespertino"),
            Estudiante(persona_id=52, carnet_estudiante="2022-678U", area_conocimiento_id=area_conocimiento.id, carrera="Industrial", ano_academico=3, grupo="3S5-IND", turno="Sabatino"),
            Estudiante(persona_id=53, carnet_estudiante="2021-901I", area_conocimiento_id=area_conocimiento.id, carrera="Química", ano_academico=4, grupo="4M7-QUI", turno="Matutino"),
            Estudiante(persona_id=54, carnet_estudiante="2023-234U", area_conocimiento_id=area_conocimiento.id, carrera="Arquitectura", ano_academico=2, grupo="2T4-ARQ", turno="Vespertino"),
            Estudiante(persona_id=55, carnet_estudiante="2020-567I", area_conocimiento_id=area_conocimiento.id, carrera="Sistemas", ano_academico=5, grupo="5S6-SIS", turno="Sabatino"),
            Estudiante(persona_id=56, carnet_estudiante="2022-890U", area_conocimiento_id=area_conocimiento.id, carrera="Computación", ano_academico=3, grupo="3M8-COM", turno="Matutino"),
            Estudiante(persona_id=57, carnet_estudiante="2021-123I", area_conocimiento_id=area_conocimiento.id, carrera="Civil", ano_academico=4, grupo="4T7-CIV", turno="Vespertino"),
            Estudiante(persona_id=58, carnet_estudiante="2023-456U", area_conocimiento_id=area_conocimiento.id, carrera="Electrónica", ano_academico=2, grupo="2S4-ELE", turno="Sabatino"),
            Estudiante(persona_id=59, carnet_estudiante="2020-789I", area_conocimiento_id=area_conocimiento.id, carrera="Industrial", ano_academico=5, grupo="5M5-IND", turno="Matutino"),
            Estudiante(persona_id=60, carnet_estudiante="2022-012U", area_conocimiento_id=area_conocimiento.id, carrera="Química", ano_academico=3, grupo="3T8-QUI", turno="Vespertino"),
        ]
        
        db.session.add_all(estudiantes)
        db.session.commit()
        print("[OK] Estudiantes insertados")

                # ---------------------------------------------------------------------
        # 13. Insertar Actividades
        # ---------------------------------------------------------------------
        # Obtener referencias necesarias
        tipo_campana = TipoActividad.query.filter_by(nombre="Campaña").first()
        tipo_capacitacion = TipoActividad.query.filter_by(nombre="Capacitación").first()
        tipo_conferencia = TipoActividad.query.filter_by(nombre="Conferencia").first()
        tipo_taller = TipoActividad.query.filter_by(nombre="Taller").first()
        tipo_foro = TipoActividad.query.filter_by(nombre="Foro").first()
        tipo_seminario = TipoActividad.query.filter_by(nombre="Seminario").first()
        tipo_competencia = TipoActividad.query.filter_by(nombre="Competencia").first()
        tipo_conversatorio = TipoActividad.query.filter_by(nombre="Conversatorio").first()
        tipo_feria = TipoActividad.query.filter_by(nombre="Feria").first()
        tipo_coloquio = TipoActividad.query.filter_by(nombre="Coloquio").first()
        tipo_simposio = TipoActividad.query.filter_by(nombre="Simposio").first()
        
        # Unidades responsables
        unidad_rectoria = UnidadOrganizativa.query.filter_by(codigo="EDU").first()
        unidad_academica = UnidadOrganizativa.query.filter_by(codigo="ART").first()
        unidad_calidad = UnidadOrganizativa.query.filter_by(codigo="CSOC").first()
        
        # Usuarios
        user_encargado = Usuario.query.filter_by(email="encargado@uni.edu.ni").first()
        user_rector = Usuario.query.filter_by(email="rector@uni.edu.ni").first()
        
        # Espacios físicos
        espacio_auditorio_salomon = EspacioFisico.query.filter_by(nombre="Auditorio Salomón de la Selva").first()
        espacio_sala_ruben = EspacioFisico.query.filter_by(nombre="Sala Rubén Darío").first()
        espacio_biblioteca_rusb = EspacioFisico.query.filter_by(nombre="Biblioteca", sede_id=sede_rusb.id).first()
        espacio_sala_blanca = EspacioFisico.query.filter_by(nombre="Sala Blanca Arauz").first()
        espacio_sala_prokrainse = EspacioFisico.query.filter_by(nombre="Sala Prokrainse").first()
        espacio_auditorio_areito = EspacioFisico.query.filter_by(nombre="Auditorio Areíto").first()
        espacio_biblioteca_rupap = EspacioFisico.query.filter_by(nombre="Biblioteca", sede_id=sede_rupap.id).first()
        espacio_auditorio_aldoumbiva = EspacioFisico.query.filter_by(nombre="Auditorio Aldo Umbiva").first()
        
        actividades = [
            # Actividad 1: Campana de Valores y Convivencia
            Actividad(
                codigo_actividad="ACT-2024-001",
                nombre="Campana de Valores y Convivencia",
                tipo_actividad_id=tipo_campana.id,
                unidad_responsable_id=unidad_rectoria.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=espacio_biblioteca_rusb.id,
                proposito="Promover la practica de valores de solidaridad, respeto y no violencia en la comunidad universitaria",
                imagen_url=None,
                fecha_inicio=datetime(2024, 9, 1),
                fecha_fin=datetime(2024, 9, 30),
                hora_inicio="08:00",
                hora_fin="17:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 2: Capacitacion en Evaluacion Formativa para Docentes
            Actividad(
                codigo_actividad="ACT-2024-002",
                nombre="Capacitacion en Evaluacion Formativa para Docentes",
                tipo_actividad_id=tipo_capacitacion.id,
                unidad_responsable_id=unidad_academica.id,
                usuario_creador_id=user_rector.id,
                espacio_fisico_id=espacio_auditorio_areito.id,
                proposito="Fortalecer las capacidades docentes en metodologias de evaluacion formativa y significativa",
                imagen_url=None,
                fecha_inicio=datetime(2024, 9, 5),
                fecha_fin=datetime(2024, 9, 6),
                hora_inicio="09:00",
                hora_fin="16:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 3: Conferencia: Inteligencia Artificial en la Educacion Superior
            Actividad(
                codigo_actividad="ACT-2024-003",
                nombre="Conferencia: Inteligencia Artificial en la Educacion Superior",
                tipo_actividad_id=tipo_conferencia.id,
                unidad_responsable_id=unidad_academica.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=espacio_auditorio_salomon.id,
                proposito="Explorar el impacto y las aplicaciones de la IA en los procesos de ensenanza y aprendizaje universitario",
                imagen_url=None,
                fecha_inicio=datetime(2024, 9, 10),
                fecha_fin=datetime(2024, 9, 10),
                hora_inicio="10:00",
                hora_fin="13:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 4: Taller de Innovacion Pedagogica con Tecnologias Educativas
            Actividad(
                codigo_actividad="ACT-2024-004",
                nombre="Taller de Innovacion Pedagogica con Tecnologias Educativas",
                tipo_actividad_id=tipo_taller.id,
                unidad_responsable_id=unidad_academica.id,
                usuario_creador_id=user_rector.id,
                espacio_fisico_id=espacio_sala_ruben.id,
                proposito="Disenar e implementar estrategias innovadoras para la ensenanza con herramientas digitales",
                imagen_url=None,
                fecha_inicio=datetime(2024, 9, 12),
                fecha_fin=datetime(2024, 9, 13),
                hora_inicio="14:00",
                hora_fin="18:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 5: Foro: Calidad Educativa y Acreditacion Universitaria
            Actividad(
                codigo_actividad="ACT-2024-005",
                nombre="Foro: Calidad Educativa y Acreditacion Universitaria",
                tipo_actividad_id=tipo_foro.id,
                unidad_responsable_id=unidad_calidad.id,
                usuario_creador_id=user_rector.id,
                espacio_fisico_id=espacio_auditorio_aldoumbiva.id,
                proposito="Analizar los desafios y oportunidades para la mejora continua de la calidad educativa en la UNI",
                imagen_url=None,
                fecha_inicio=datetime(2024, 9, 15),
                fecha_fin=datetime(2024, 9, 15),
                hora_inicio="09:00",
                hora_fin="12:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 6: Seminario de Investigacion e Innovacion Tecnologica
            Actividad(
                codigo_actividad="ACT-2024-006",
                nombre="Seminario de Investigacion e Innovacion Tecnologica",
                tipo_actividad_id=tipo_seminario.id,
                unidad_responsable_id=unidad_academica.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=espacio_auditorio_salomon.id,
                proposito="Presentar y discutir proyectos de investigacion e innovacion desarrollados por estudiantes y docentes",
                imagen_url=None,
                fecha_inicio=datetime(2024, 9, 18),
                fecha_fin=datetime(2024, 9, 20),
                hora_inicio="08:30",
                hora_fin="17:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 7: Jornada de Cuido y Conservacion del Agua
            Actividad(
                codigo_actividad="ACT-2024-007",
                nombre="Jornada de Cuido y Conservacion del Agua",
                tipo_actividad_id=TipoActividad.query.filter_by(nombre="Jornada").first().id,
                unidad_responsable_id=unidad_rectoria.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=espacio_biblioteca_rusb.id,
                proposito="Concientizar sobre la importancia del agua como recurso vital y promover su conservacion",
                imagen_url=None,
                fecha_inicio=datetime(2024, 9, 23),
                fecha_fin=datetime(2024, 9, 23),
                hora_inicio="08:00",
                hora_fin="12:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 8: Competencia de Programacion y Desarrollo de Software
            Actividad(
                codigo_actividad="ACT-2024-008",
                nombre="Competencia de Programacion y Desarrollo de Software",
                tipo_actividad_id=tipo_competencia.id,
                unidad_responsable_id=unidad_academica.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=espacio_sala_ruben.id,
                proposito="Fomentar el desarrollo de habilidades de programacion y resolucion de problemas en estudiantes",
                imagen_url=None,
                fecha_inicio=datetime(2024, 9, 25),
                fecha_fin=datetime(2024, 9, 26),
                hora_inicio="09:00",
                hora_fin="18:00",
                asistencia_abierta=False,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 9: Conversatorio: Historia e Identidad Nacional
            Actividad(
                codigo_actividad="ACT-2024-009",
                nombre="Conversatorio: Historia e Identidad Nacional",
                tipo_actividad_id=tipo_conversatorio.id,
                unidad_responsable_id=unidad_rectoria.id,
                usuario_creador_id=user_rector.id,
                espacio_fisico_id=espacio_sala_ruben.id,
                proposito="Reflexionar sobre la historia de lucha y la identidad cultural de Nicaragua",
                imagen_url=None,
                fecha_inicio=datetime(2024, 9, 28),
                fecha_fin=datetime(2024, 9, 28),
                hora_inicio="15:00",
                hora_fin="18:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 10: Feria de Creatividad e Innovacion UNI 2024
            Actividad(
                codigo_actividad="ACT-2024-010",
                nombre="Feria de Creatividad e Innovacion UNI 2024",
                tipo_actividad_id=tipo_feria.id,
                unidad_responsable_id=unidad_academica.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=espacio_biblioteca_rusb.id,
                proposito="Exhibir proyectos innovadores y creativos desarrollados por estudiantes de todas las carreras",
                imagen_url=None,
                fecha_inicio=datetime(2024, 10, 1),
                fecha_fin=datetime(2024, 10, 3),
                hora_inicio="09:00",
                hora_fin="17:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 11: Coloquio de Investigacion Cientifica
            Actividad(
                codigo_actividad="ACT-2024-011",
                nombre="Coloquio de Investigacion Cientifica",
                tipo_actividad_id=tipo_coloquio.id,
                unidad_responsable_id=unidad_calidad.id,
                usuario_creador_id=user_rector.id,
                espacio_fisico_id=espacio_auditorio_salomon.id,
                proposito="Presentar avances de investigacion cientifica en las areas de ingenieria y tecnologia",
                imagen_url=None,
                fecha_inicio=datetime(2024, 10, 5),
                fecha_fin=datetime(2024, 10, 5),
                hora_inicio="09:00",
                hora_fin="16:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 12: Capacitacion Intensiva de Ingles para Docentes
            Actividad(
                codigo_actividad="ACT-2024-012",
                nombre="Capacitacion Intensiva de Ingles para Docentes",
                tipo_actividad_id=tipo_capacitacion.id,
                unidad_responsable_id=unidad_academica.id,
                usuario_creador_id=user_rector.id,
                espacio_fisico_id=espacio_auditorio_areito.id,
                proposito="Fortalecer las habilidades linguisticas en ingles de docentes para la ensenanza bilingue",
                imagen_url=None,
                fecha_inicio=datetime(2024, 10, 7),
                fecha_fin=datetime(2024, 10, 11),
                hora_inicio="08:00",
                hora_fin="12:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 13: Festival Cultural y Artístico UNI
            Actividad(
                codigo_actividad="ACT-2024-013",
                nombre="Festival Cultural y Artistico UNI",
                tipo_actividad_id=TipoActividad.query.filter_by(nombre="Festival").first().id,
                unidad_responsable_id=unidad_rectoria.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=espacio_biblioteca_rupap.id,
                proposito="Promover las expresiones artisticas y culturales de la comunidad universitaria",
                imagen_url=None,
                fecha_inicio=datetime(2024, 10, 12),
                fecha_fin=datetime(2024, 10, 12),
                hora_inicio="10:00",
                hora_fin="20:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 14: Simposio Internacional de Gestion de Calidad
            Actividad(
                codigo_actividad="ACT-2024-014",
                nombre="Simposio Internacional de Gestion de Calidad",
                tipo_actividad_id=tipo_simposio.id,
                unidad_responsable_id=unidad_calidad.id,
                usuario_creador_id=user_rector.id,
                espacio_fisico_id=espacio_auditorio_aldoumbiva.id,
                proposito="Compartir experiencias y buenas practicas en gestion de calidad educativa a nivel internacional",
                imagen_url=None,
                fecha_inicio=datetime(2024, 10, 15),
                fecha_fin=datetime(2024, 10, 17),
                hora_inicio="09:00",
                hora_fin="17:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
            # Actividad 15: Jornada de Habitos Saludables y Deporte
            Actividad(
                codigo_actividad="ACT-2024-015",
                nombre="Jornada de Habitos Saludables y Deporte",
                tipo_actividad_id=TipoActividad.query.filter_by(nombre="Jornada").first().id,
                unidad_responsable_id=unidad_rectoria.id,
                usuario_creador_id=user_encargado.id,
                espacio_fisico_id=espacio_sala_prokrainse.id,
                proposito="Fomentar la practica de habitos saludables y la actividad fisica en la comunidad universitaria",
                imagen_url=None,
                fecha_inicio=datetime(2024, 10, 20),
                fecha_fin=datetime(2024, 10, 20),
                hora_inicio="07:00",
                hora_fin="12:00",
                asistencia_abierta=True,
                is_synced=False,
                created_offline=False,
                updated_at=datetime(2026, 8, 16, 23, 2, 6)
            ),
        ]
        
        db.session.add_all(actividades)
        db.session.commit()
        print("[OK] Actividades insertadas")

        # ---------------------------------------------------------------------
        # 14. Insertar ActividadLineamiento
        # ---------------------------------------------------------------------
        # Obtener referencias a las actividades
        act_dict = {act.codigo_actividad: act for act in Actividad.query.all()}
        
        # Obtener referencias a los lineamientos por su número oficial
        lineamiento_dict = {l.numero_oficial: l for l in Lineamiento.query.all()}
        
        actividad_lineamientos = [
            # Actividad 1: Campana de Valores y Convivencia
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-001"].id,
                lineamiento_id=lineamiento_dict["2.1"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-001"].id,
                lineamiento_id=lineamiento_dict["2.3"].id
            ),
            # Actividad 2: Capacitacion en Evaluacion Formativa para Docentes
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-002"].id,
                lineamiento_id=lineamiento_dict["13.2"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-002"].id,
                lineamiento_id=lineamiento_dict["14.2"].id
            ),
            # Actividad 3: Conferencia: Inteligencia Artificial en la Educacion Superior
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-003"].id,
                lineamiento_id=lineamiento_dict["13.5"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-003"].id,
                lineamiento_id=lineamiento_dict["15.1"].id
            ),
            # Actividad 4: Taller de Innovacion Pedagogica con Tecnologias Educativas
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-004"].id,
                lineamiento_id=lineamiento_dict["11.3"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-004"].id,
                lineamiento_id=lineamiento_dict["13.6"].id
            ),
            # Actividad 5: Foro: Calidad Educativa y Acreditacion Universitaria
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-005"].id,
                lineamiento_id=lineamiento_dict["13.7"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-005"].id,
                lineamiento_id=lineamiento_dict["13.8"].id
            ),
            # Actividad 6: Seminario de Investigacion e Innovacion Tecnologica
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-006"].id,
                lineamiento_id=lineamiento_dict["11.1"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-006"].id,
                lineamiento_id=lineamiento_dict["11.2"].id
            ),
            # Actividad 7: Jornada de Cuido y Conservacion del Agua
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-007"].id,
                lineamiento_id=lineamiento_dict["6.1"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-007"].id,
                lineamiento_id=lineamiento_dict["6.2"].id
            ),
            # Actividad 8: Competencia de Programacion y Desarrollo de Software
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-008"].id,
                lineamiento_id=lineamiento_dict["1.7"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-008"].id,
                lineamiento_id=lineamiento_dict["11.8"].id
            ),
            # Actividad 9: Conversatorio: Historia e Identidad Nacional
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-009"].id,
                lineamiento_id=lineamiento_dict["5.1"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-009"].id,
                lineamiento_id=lineamiento_dict["5.3"].id
            ),
            # Actividad 10: Feria de Creatividad e Innovacion UNI 2024
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-010"].id,
                lineamiento_id=lineamiento_dict["3.1"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-010"].id,
                lineamiento_id=lineamiento_dict["11.2"].id
            ),
            # Actividad 11: Coloquio de Investigacion Cientifica
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-011"].id,
                lineamiento_id=lineamiento_dict["10.1"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-011"].id,
                lineamiento_id=lineamiento_dict["11.7"].id
            ),
            # Actividad 12: Capacitacion Intensiva de Ingles para Docentes
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-012"].id,
                lineamiento_id=lineamiento_dict["1.8"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-012"].id,
                lineamiento_id=lineamiento_dict["14.2"].id
            ),
            # Actividad 13: Festival Cultural y Artístico UNI
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-013"].id,
                lineamiento_id=lineamiento_dict["4.1"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-013"].id,
                lineamiento_id=lineamiento_dict["4.4"].id
            ),
            # Actividad 14: Simposio Internacional de Gestion de Calidad
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-014"].id,
                lineamiento_id=lineamiento_dict["13.7"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-014"].id,
                lineamiento_id=lineamiento_dict["13.8"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-014"].id,
                lineamiento_id=lineamiento_dict["15.4"].id
            ),
            # Actividad 15: Jornada de Habitos Saludables y Deporte
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-015"].id,
                lineamiento_id=lineamiento_dict["1.9"].id
            ),
            ActividadLineamiento(
                actividad_id=act_dict["ACT-2024-015"].id,
                lineamiento_id=lineamiento_dict["8.1"].id
            ),
        ]
        
        db.session.add_all(actividad_lineamientos)
        db.session.commit()
        print("[OK] ActividadLineamientos insertados")

                # ---------------------------------------------------------------------
        # 15. Insertar Asistencias
        # ---------------------------------------------------------------------
        # Obtener referencias a las actividades
        act_dict = {act.codigo_actividad: act for act in Actividad.query.all()}

        # Obtener usuario registrador (el encargado)
        usuario_registrador = Usuario.query.filter_by(email="encargado@uni.edu.ni").first()
        if not usuario_registrador:
            usuario_registrador = Usuario.query.first()

        # --- Asistencias de estudiantes (datos proporcionados) ---
        # Mapear persona_id a persona_id (estudiante usa persona_id como PK)
        estudiante_persona_ids = [e.persona_id for e in Estudiante.query.all()]

        # Función para crear timestamp ISO
        def to_iso(dt):
            return dt.isoformat() + "Z" if dt.tzinfo is None else dt.isoformat()

        asistencias_estudiantes = [
            # Actividad 1: ACT-2024-001
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="1",  # María José González Pérez
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 8, 15, 23)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="3",  # Ana Lucía Ramírez Castro
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 9, 30, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="5",  # Laura Elena Sánchez Rivera
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 3, 10, 0, 12)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="7",  # Diana Carolina Flores Mena
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 8, 45, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="9",  # Patricia Isabel Vega Solís
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 3, 11, 20, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="11",  # Carmen Elena Herrera Sánchez
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 10, 10, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="13",  # Rosa María Chavarría López
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 4, 9, 0, 0)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="15",  # Lorena Beatriz Rojas Navarro
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 8, 30, 55)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="17",  # Sofía Alejandra Gutiérrez Morales
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 3, 14, 15, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="19",  # Elena Cristina Calderón Zamora
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 9, 50, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="21",  # Karla Paola Vanegas Sandoval
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 4, 8, 20, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="23",  # María Fernanda Zelaya Barrios
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 3, 10, 30, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="25",  # Gabriela Esther Pereira Calero
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 11, 5, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="27",  # Natalia Isabel Baca Barrera
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 4, 9, 40, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="29",  # Adriana Beatriz Solórzano Morales
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 8, 55, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="31",  # Cynthia Marcela Membreño Narváez
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 3, 13, 20, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="33",  # Paola Andrea Fletes Mendoza
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 10, 45, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="35",  # Mónica Lisseth Vivas Téllez
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 4, 8, 10, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="37",  # Silvia Elena Cuadra Fonseca
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 9, 15, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="39",  # Jackeline María Rocha Martínez
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 3, 15, 30, 20)),
                is_synced=1
            ),
            # Actividad 2: ACT-2024-002
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="2",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 14, 20, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="4",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 15, 45, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="6",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 7, 9, 10, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="8",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 10, 30, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="10",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 7, 11, 50, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="12",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 8, 40, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="14",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 7, 13, 15, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="16",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 16, 30, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="18",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 7, 9, 45, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="20",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 14, 55, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="22",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 8, 8, 20, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="24",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 12, 10, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="26",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 7, 15, 35, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="28",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 9, 20, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="30",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 8, 10, 5, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="32",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 11, 30, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="34",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 7, 8, 50, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="36",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 13, 40, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="38",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 8, 9, 25, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="40",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 15, 10, 20)),
                is_synced=1
            ),
            # Actividad 3: ACT-2024-003
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="1",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 10, 15, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="3",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 11, 30, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="5",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 12, 45, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="7",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 10, 40, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="9",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 11, 15, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="11",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 9, 50, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="13",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 13, 5, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="15",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 10, 25, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="17",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 12, 10, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="19",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 11, 40, 35)),
                is_synced=1
            ),
            # Actividad 4: ACT-2024-004
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="2",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 13, 14, 30, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="4",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 13, 15, 45, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="6",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 12, 9, 10, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="8",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 13, 16, 20, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="10",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 12, 10, 35, 25)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="12",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 13, 14, 55, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="14",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 12, 11, 20, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="16",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 13, 15, 10, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="18",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 12, 9, 45, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="20",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 13, 16, 40, 35)),
                is_synced=1
            ),
            # Actividad 5: ACT-2024-005
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="1",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 9, 20, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="3",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 10, 45, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="5",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 11, 30, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="7",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 9, 50, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="9",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 10, 15, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="11",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 12, 0, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="13",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 9, 35, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="15",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 11, 45, 55)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="17",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 10, 30, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="19",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 12, 15, 40)),
                is_synced=1
            ),
            # Actividad 6: ACT-2024-006
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="2",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 19, 9, 30, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="4",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 19, 10, 45, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="6",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 18, 11, 20, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="8",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 19, 14, 15, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="10",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 18, 9, 45, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="12",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 19, 15, 30, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="14",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 18, 10, 10, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="16",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 19, 8, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="18",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 18, 13, 40, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="20",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 19, 16, 5, 45)),
                is_synced=1
            ),
            # Actividad 7: ACT-2024-007
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="1",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 8, 15, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="3",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 9, 30, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="5",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 10, 45, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="7",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 8, 50, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="9",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 11, 20, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="11",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 9, 15, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="13",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 10, 30, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="15",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 8, 40, 50)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="17",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 12, 0, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="19",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 9, 55, 15)),
                is_synced=1
            ),
            # Actividad 8: ACT-2024-008
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="2",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 25, 9, 20, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="4",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 25, 10, 45, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="6",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 26, 11, 30, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="8",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 25, 14, 15, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="10",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 26, 9, 45, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="12",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 25, 15, 30, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="14",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 26, 10, 20, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="16",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 25, 8, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="18",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 26, 13, 40, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="20",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 25, 16, 5, 45)),
                is_synced=1
            ),
            # Actividad 9: ACT-2024-009
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="1",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 15, 30, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="3",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 16, 45, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="5",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 17, 20, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="7",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 15, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="9",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 16, 10, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="11",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 17, 45, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="13",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 15, 40, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="15",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 16, 30, 50)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="17",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 17, 55, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="19",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 15, 15, 45)),
                is_synced=1
            ),
            # Actividad 10: ACT-2024-010
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="2",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 1, 9, 20, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="4",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 1, 10, 45, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="6",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 2, 11, 30, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="8",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 1, 14, 15, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="10",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 2, 9, 45, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="12",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 1, 15, 30, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="14",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 2, 10, 20, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="16",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 1, 8, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="18",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 2, 13, 40, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="20",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 1, 16, 5, 45)),
                is_synced=1
            ),
            # Actividad 11: ACT-2024-011
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="1",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 9, 30, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="3",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 10, 45, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="5",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 11, 20, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="7",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 9, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="9",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 10, 30, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="11",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 12, 15, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="13",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 9, 15, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="15",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 11, 40, 50)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="17",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 10, 5, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="19",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 12, 45, 15)),
                is_synced=1
            ),
            # Actividad 12: ACT-2024-012
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="2",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 8, 9, 30, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="4",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 8, 10, 45, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="6",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 7, 11, 20, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="8",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 8, 14, 15, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="10",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 7, 9, 45, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="12",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 8, 15, 30, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="14",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 7, 10, 20, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="16",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 8, 8, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="18",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 7, 13, 40, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="20",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 8, 16, 5, 45)),
                is_synced=1
            ),
            # Actividad 13: ACT-2024-013
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="1",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 10, 30, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="3",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 11, 45, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="5",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 12, 20, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="7",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 10, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="9",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 11, 30, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="11",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 13, 15, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="13",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 10, 15, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="15",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 12, 40, 50)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="17",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 11, 5, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="19",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 13, 45, 15)),
                is_synced=1
            ),
            # Actividad 14: ACT-2024-014
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="2",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 16, 9, 30, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="4",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 16, 10, 45, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="6",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 15, 11, 20, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="8",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 16, 14, 15, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="10",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 15, 9, 45, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="12",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 16, 15, 30, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="14",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 15, 10, 20, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="16",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 16, 8, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="18",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 15, 13, 40, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="20",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 16, 16, 5, 45)),
                is_synced=1
            ),
            # Actividad 15: ACT-2024-015
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="1",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 8, 15, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="3",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 9, 30, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="5",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 10, 45, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="7",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 8, 50, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="9",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 11, 20, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="11",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 9, 15, 45)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="13",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 10, 30, 35)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="15",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 8, 40, 50)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="17",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 12, 0, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="19",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 9, 55, 15)),
                is_synced=1
            ),
        ]

        db.session.add_all(asistencias_estudiantes)
        db.session.commit()
        print("[OK] Asistencias de estudiantes insertadas (170 registros)")

        # --- Asistencias de trabajadores (datos generados) ---
        # Obtener IDs de trabajadores (personas que tienen registro en Trabajador)
        trabajador_persona_ids = [t.persona_id for t in Trabajador.query.all()]
        # Seleccionar algunos trabajadores para las asistencias
        trabajadores_seleccionados = list(range(61, 81)) + [1, 5, 10, 15, 20, 25, 30, 35, 40]

        asistencias_trabajadores = [
            # Actividad 1: ACT-2024-001
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="61",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 8, 20, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="63",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 3, 9, 15, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="65",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 10, 40, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="67",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 4, 8, 50, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="69",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 3, 11, 30, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="1",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 2, 9, 0, 0)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-001"].id,
                persona_id="10",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 3, 14, 30, 20)),
                is_synced=1
            ),
            # Actividad 2: ACT-2024-002
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="62",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 14, 40, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="64",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 7, 9, 20, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="66",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 15, 50, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="68",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 8, 10, 10, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="70",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 6, 11, 30, 10)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-002"].id,
                persona_id="5",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 7, 13, 45, 30)),
                is_synced=1
            ),
            # Actividad 3: ACT-2024-003
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="71",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 10, 30, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="73",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 11, 45, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="75",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 12, 30, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-003"].id,
                persona_id="15",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 10, 13, 10, 30)),
                is_synced=1
            ),
            # Actividad 4: ACT-2024-004
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="72",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 13, 14, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="74",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 12, 9, 30, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="76",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 13, 16, 20, 40)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-004"].id,
                persona_id="20",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 12, 10, 45, 10)),
                is_synced=1
            ),
            # Actividad 5: ACT-2024-005
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="77",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 9, 40, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="79",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 10, 55, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-005"].id,
                persona_id="25",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 15, 11, 10, 40)),
                is_synced=1
            ),
            # Actividad 6: ACT-2024-006
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="78",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 19, 9, 50, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="80",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 18, 11, 40, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-006"].id,
                persona_id="30",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 19, 15, 20, 10)),
                is_synced=1
            ),
            # Actividad 7: ACT-2024-007
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="61",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 8, 30, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="63",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 10, 40, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-007"].id,
                persona_id="35",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 22, 9, 20, 30)),
                is_synced=1
            ),
            # Actividad 8: ACT-2024-008
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="65",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 25, 9, 40, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="67",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 26, 14, 20, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-008"].id,
                persona_id="40",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 25, 15, 50, 10)),
                is_synced=1
            ),
            # Actividad 9: ACT-2024-009
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="69",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 15, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="71",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 17, 10, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-009"].id,
                persona_id="1",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 9, 28, 16, 20, 40)),
                is_synced=1
            ),
            # Actividad 10: ACT-2024-010
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="73",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 1, 9, 30, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="75",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 2, 10, 50, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-010"].id,
                persona_id="10",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 1, 14, 30, 10)),
                is_synced=1
            ),
            # Actividad 11: ACT-2024-011
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="77",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 9, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="79",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 11, 20, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-011"].id,
                persona_id="15",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 5, 12, 40, 40)),
                is_synced=1
            ),
            # Actividad 12: ACT-2024-012
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="62",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 8, 9, 50, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="64",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 7, 11, 30, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-012"].id,
                persona_id="20",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 8, 15, 40, 10)),
                is_synced=1
            ),
            # Actividad 13: ACT-2024-013
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="66",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 10, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="68",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 12, 30, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-013"].id,
                persona_id="25",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 12, 13, 10, 40)),
                is_synced=1
            ),
            # Actividad 14: ACT-2024-014
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="70",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 16, 9, 40, 15)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="72",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 15, 10, 50, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-014"].id,
                persona_id="30",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 16, 14, 30, 10)),
                is_synced=1
            ),
            # Actividad 15: ACT-2024-015
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="74",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 8, 30, 30)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="76",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 10, 20, 20)),
                is_synced=1
            ),
            Asistencia(
                actividad_id=act_dict["ACT-2024-015"].id,
                persona_id="35",
                usuario_registrador_id=usuario_registrador.id,
                timestamp_registro=to_iso(datetime(2024, 10, 19, 9, 40, 40)),
                is_synced=1
            ),
        ]

        db.session.add_all(asistencias_trabajadores)
        db.session.commit()
        print("[OK] Asistencias de trabajadores insertadas (52 registros)")

if __name__ == "__main__":
    seed_database()