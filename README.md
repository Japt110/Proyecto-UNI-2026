# Plataforma de Gestión de Eventos y Asistencia Universitaria (Eventos-UNI)

Sistema web integral desarrollado para la **Universidad Nacional de Ingeniería (UNI)** destinado al registro, administración, toma de asistencia y análisis estadístico en tiempo real de actividades académicas e institucionales.

---

## 🏛️ Arquitectura y Principios de Diseño

El sistema está diseñado bajo una **arquitectura en 4 capas desacoplada** orientada a la mantenibilidad, escalabilidad y alta disponibilidad local (*Offline-First*), resolviendo el dilema del **Teorema CAP** al combinar consistencia transaccional central con tolerancia total a fallos en campo:

1. **Capa 1: Frontera de Cliente y Persistencia Local (Offline-First)**:
   - Backend modular en Python 3.13 con Flask utilizando el patrón **Application Factory** y **Blueprints**.
   - Persistencia local mediante **SQLite 3 (`app_local.db`)** para operación ininterrumpida en recintos sin conectividad continua.
   - Generación de identificadores universales únicos (**UUID v4**) en local y banderas de sincronización (`is_synced`, `created_offline`).
   - Frontend reactivo y moderno construido en **Vanilla JS (ES6+)**, HTML5 semántico y CSS3 con sistema de tokens de diseño.
2. **Capa 2: Perímetro de Red y Seguridad (DMZ)**:
   - Nginx API Gateway y WAF perimetral que efectúa balanceo de carga Round-Robin / `least_conn`, compresión gzip, control de tasa (*Rate Limiting*) Anti-DoS e inyección de cabeceras de hardening OWASP.
3. **Capa 3: Clúster de Lógica de Negocio y Sincronización (Stateless)**:
   - Nodos concurrentes en Python 3.13 servidos por **Gunicorn WSGI (workers híbridos `gthread`)**, gestión de sesiones distribuidas y caché en **Redis**, y el motor nuclear de reconciliación transaccional UPSERT.
4. **Capa 4: Clúster de Persistencia Centralizado (5FN)**:
   - Clúster relacional **PostgreSQL 16** (o **Supabase**) con 22 tablas normalizadas en **5ª Forma Normal (5FN)**, arquitectura Write Master / Read Replica con replicación asíncrona WAL.

### 🛡️ Seguridad y Hardening (OWASP Standards):
- Hashing seguro de contraseñas mediante **PBKDF2:SHA256** con *salt* dinámico de 16 bytes.
- Autenticación persistente por **Tokens de Sesión HMAC-SHA256** (`Authorization: Bearer <session_token>` y `X-Session-Token`) con validez de 8 horas, permitiendo recarga de página (`Ctrl+R`) sin solicitar credenciales constantemente.
- Invalidación automática e instantánea de la caché del navegador (`ClientCache.invalidateAll()`) al iniciar o cerrar sesión para prevenir visualización de datos de sesiones expiradas.
- Control de Acceso Basado en Roles (**RBAC**) mediante decoradores middleware a nivel de servidor (`@login_required`, `@roles_required`).
- Telemetría automática en cada solicitud registrando latencia exacta en milisegundos (`X-Response-Time-Ms`) y persistencia en `registro_consultas`.
- Límite estricto de carga por payload (16 MB) y sanitización preventiva de entradas JSON.

---

## 🚀 Funcionalidades Principales

1. **Autenticación Polimórfica Integrada**:
   - Inicio de sesión seguro identificando usuarios mediante Correo Electrónico Institucional, Cédula de Identidad, Carné de Estudiante o Código de Trabajador.
2. **Gestión de Eventos y Proyectos Científicos (CRUD)**:
   - Registro, consulta, filtrado dinámico y edición de actividades universitarias (Ferias, Conferencias, Talleres, Simposios).
   - Generación local de identificadores universales únicos (**UUID**) para soporte de creación fuera de línea.
   - Botones de transición de estado manual (`Activar actividad` y `Finalizar actividad`) con preservación de eventos en carrusel.
   - Alineación obligatoria a los Ejes, Lineamientos y Acciones de la **Estrategia Nacional de Educación 2026**.
3. **Control y Toma de Asistencia de Alta Concurrencia**:
   - Soporte nativo para escáneres de código de barras USB HID (ej. **3nStar Sc050**).
   - Buscador automático en tiempo real con debounce (250ms) y detección automática de duplicados (`✓ Registrado` con botón `Ubicar en Tabla` para desplazamiento suave).
   - Validaciones estrictas de padrón 5FN: **Cédula Nicaragüense** con verificación Módulo 23 en base 10 y letra intocable, **Carné** (`0000-0000X`), **NUP** y **Grupo** (`ATN-XXX-XXX` con separación automática tras el 2do trío de 3 letras).
   - Tabla de asistencia con **selección múltiple** (`Ctrl + Click` para selección individual, `Shift + Click` para rangos) y botón único externo de eliminación masiva con confirmación.
   - Cierre/Reapertura de asistencia sin vaciar la lista en pantalla y panel lateral de perfil (*User Profile Drawer*) accesible desde todas las vistas.
4. **Dashboard y Estadísticas Reales 5FN por Evento**:
   - Medidor principal de **Total de Asistentes Confirmados**.
   - Agregaciones demográficas reales procesadas en SQL desde las tablas normalizadas (`Persona`, `Estudiante`, `Trabajador`) con desgloses por **Carrera Profesional**, **Grupo**, **Género**, **Rol Institucional** y **Año Académico**.
5. **Motor de Reconciliación Transaccional y Sincronización Distribuida**:
   - Algoritmo **Last-Write-Wins (LWW)** por marcas temporales `updated_at` (ISO 8601 UTC).
   - Idempotencia garantizada en marcas de asistencia evitando duplicados en retransmisiones de red.
   - Propagación de bajas con marcadores inmutables (**Tombstones**) y cálculo de deltas del servidor (**Pull Delta**).

---

## 🗄️ Modelo Relacional en 5ª Forma Normal (22 Tablas)

El modelo elimina toda anomalía de redundancia mediante herencia relacional 1:1 en el padrón universitario y tablas dedicadas de infraestructura distribuida:

| Dominio | Tablas Físicas | Propósito Arquitectónico |
|---|---|---|
| **Geografía y Sedes** | `departamentos`, `ciudades`, `sedes`, `espacios_fisicos` | Catálogos de división territorial y recintos físicos universitarios. |
| **Estructura Organizacional** | `unidades_organizativas` | Facultades, direcciones y jerarquía institucional. |
| **Padrón 5FN (Herencia 1:1)** | `personas`, `estudiantes`, `trabajadores`, `usuarios` | Supertipo `Persona` con especializaciones 1:1 compartiendo PK como FK en cascada. |
| **Estrategia Nacional 2026** | `ejes_lineamiento`, `lineamientos`, `acciones_estrategicas` | Estructura jerárquica de alineación a la política educativa nacional. |
| **Eventos y Asistencia** | `tipos_actividad`, `actividades`, `actividades_lineamientos`, `asistencias` | CRUD de eventos, asignación N:M con justificación y marcas atómicas. |
| **Clúster y Sincronización** | `nodos_cliente`, `lotes_sincronizacion`, `conflictos_sincronizacion`, `bitacoras_acciones`, `tombstones`, `registro_consultas` | Registro de terminales, lotes batch, detección de colisiones JSONB, auditoría forense inmutable, marcadores de baja (*Tombstones*) y telemetría de latencia. |

---

## 📁 Estructura del Proyecto

```text
Eventos-UNI-main/
│
├── core/                           # Módulo Core de Seguridad y Lógica Distribuida
│   ├── __init__.py                 # Exportaciones centralizadas del núcleo
│   ├── security.py                 # Hashing PBKDF2, tokens HMAC y middleware RBAC
│   ├── sync_engine.py              # Motor de reconciliación transaccional UPSERT
│   └── validators.py               # Módulo 23, validaciones y sanitizadores
│
├── middleware/                     # Capa 2: Perímetro y Telemetría
│   ├── __init__.py                 # Exportación de middlewares
│   ├── rate_limiter.py             # Limitador de tasa por IP (Ventana Deslizante Anti-DoS)
│   ├── audit_logger.py             # Telemetría de latencia (ms) y headers OWASP
│   └── request_validator.py        # Sanitización de payloads JSON
│
├── models/                         # Capa 4: Persistencia ORM (SQLAlchemy 5FN - 22 Tablas)
│   ├── __init__.py                 # Exportación unificada de modelos
│   ├── base.py                     # Padrón: Persona (Supertipo), Estudiante, Trabajador y Usuario
│   ├── catalogos.py                # Catálogos: Sede, EspacioFisico, UnidadOrganizativa, TipoActividad
│   ├── eventos.py                  # Dominio transaccional: Actividad y Asistencia (Banderas Offline/Sync)
│   └── sync.py                     # Nodos, Lotes, Conflictos, Bitácoras, Tombstones, Consultas
│
├── routes/                         # Capa 3: Controladores y Endpoints API RESTful (Blueprints)
│   ├── __init__.py                 # Registro de Blueprints
│   ├── asistencia_api.py           # /api/asistencia (Marcación, búsqueda y gestión)
│   ├── auth_api.py                 # /api/auth (Login, Logout, Me y Tokens HMAC)
│   ├── catalogos_api.py            # /api/catalogos (Servicio de catálogos con caché)
│   ├── eventos_api.py              # /api/eventos (CRUD y transiciones de estado)
│   ├── stats_api.py                # /api/stats (Agregaciones 5FN para Dashboard)
│   ├── sync_api.py                 # /api/v1/sync (Sincronización distribuida Push/Pull)
│   ├── uploads_api.py              # /api/uploads (Subida segura de imágenes)
│   └── views.py                    # Servidor de plantillas HTML Jinja2
│
├── nginx/                          # Configuración de Servidor Web y API Gateway
│   └── nginx.conf                  # Nginx Load Balancer Round-Robin / TLS / Rate Limits
│
├── static/                         # Recursos Estáticos Frontend
│   ├── css/                        # Estilos CSS (Globales, componentes, tablas, asistencia)
│   ├── js/
│   │   ├── api-client.js           # Cliente HTTP asíncrono (fetchWithAuth y caché)
│   │   └── app.js                  # Lógica de interfaz, escáner USB HID, multi-select y gráficos
│   └── img/                        # Activos visuales e logotipos
│
├── templates/                      # Plantillas HTML5 (Vistas del Sistema)
│   ├── index.html                  # Dashboard de Mis Actividades (Encargado)
│   ├── login.html                  # Vista de autenticación polimórfica
│   ├── asistencia.html             # Vista de toma de asistencia y tabla de marcas
│   ├── crear-actividad.html        # Formulario de registro de eventos
│   ├── detalle-actividad.html      # Vista detallada, edición y estadísticas reales 5FN
│   ├── rector.html                 # Dashboard de Indicadores Rectorales
│   └── usuarios.html               # Vista del Padrón Universitario
│
├── app.py                          # Punto de entrada de la aplicación (Application Factory)
├── config.py                       # Configuración global, dual y hardening de seguridad
├── database.py                     # Instancia global de SQLAlchemy
├── extensions.py                   # Instancia global de Flask-Caching
├── Dockerfile                      # Contenedor multi-stage optimizado para producción
├── docker-compose.yml              # Orquestación clúster local (6 contenedores)
├── gunicorn.conf.py                # Servidor WSGI Gunicorn (workers híbridos gthread)
├── render.yaml                     # Blueprint Infrastructure-as-Code para OnRender.com
├── .env.example                    # Plantilla segura de variables de entorno para el equipo
├── test_seed.py                    # Script de semilla extendido con padrón de prueba para escáner
├── seed.py                         # Script de inicialización y datos de prueba base
├── requirements.txt                # Dependencias del proyecto Python
└── README.md                       # Documentación técnica del proyecto
```

---

## 🛠️ Instalación y Puesta en Marcha Local (Zero Config)

### Prerrequisitos
- **Python 3.10** o superior.
- Administrador de paquetes `pip`.

### 1. Clonar el repositorio e instalar dependencias

```bash
git clone https://github.com/FallenAngelLucifer/Eventos-UNI-Servicios.git
cd Eventos-UNI-Servicios

# Crear y activar entorno virtual
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

# Instalar dependencias necesarias
pip install -r requirements.txt
```

### 2. Inicializar la Base de Datos Local y Semilla de Prueba

Para poblar la base de datos local con los catálogos base, usuarios administradores y un **padrón extendido de estudiantes** ideal para pruebas de escáner USB HID (ej. **3nStar Sc050**) y búsqueda en tiempo real, ejecuta:

```bash
python test_seed.py
```

*Salida esperada:*
```text
[OK] Tablas recreadas en app_local.db
[OK] Semilla de base de datos completada exitosamente:
   - Actividades creadas: 8 actividades (Activas, Programadas y Pasadas)
   - Usuario Encargado: encargado@uni.edu.ni | Contraseña: admin123
   - Usuario Rector:    rector@uni.edu.ni    | Contraseña: rector123

[+] Insertando estudiantes de debugging en el padrón 5FN...
[OK] 10 estudiantes de prueba agregados exitosamente al padrón.

===============================================================================================
 ESTUDIANTES DISPONIBLES PARA PRUEBAS Y ESCANEO (3nStar Sc050 / BÚSQUEDA)
===============================================================================================
CÉDULA             | #NUP           | CARNÉ       | CARRERA (GRUPO)            | NOMBRES Y APELLIDOS
-----------------------------------------------------------------------------------------------
001-030704-1067H   | NUP-2026-001   | 2021-0001U  | Ingeniería Mecáni (1M1-ME) | Aaron David Díaz Martínez
001-120503-1004A   | NUP-2026-101   | 2022-0104U  | Ingeniería de Sis (4M1-CO) | María Fernanda López Jarquín
...
===============================================================================================
```

*(Nota: Si únicamente deseas los datos semilla por defecto sin estudiantes sintéticos adicionales, puedes usar `python seed.py`).*

### 3. Iniciar el Servidor Backend Local

```bash
python app.py
```

El servidor estará disponible en local en: `http://localhost:5000`

---

## 🐳 Simulación y Despliegue del Entorno Distribuido con Docker Compose

Para replicar íntegramente la arquitectura de 4 capas en un entorno aislado con balanceo de carga:

### 1. Requisitos de Infraestructura
- **Docker Engine** (24.0+) y **Docker Compose v2**.
- En entornos Windows, se recomienda **Docker Desktop** con backend **WSL 2**.

### 2. Configuración, Despliegue y Sembrado del Clúster

```bash
# 1. Generar el archivo de configuración a partir de la plantilla segura
cp .env.example .env
# (En Windows PowerShell: Copy-Item .env.example .env)

# 2. Compilar imágenes y levantar el clúster de servicios
docker-compose up --build

# 3. (Opcional) Poblar la base de datos del clúster local con la semilla de prueba
docker exec -it eventos-uni-app-1 python test_seed.py
```

#### 📦 Topología de Servicios Desplegados:
| Contenedor | Rol Arquitectónico | Puerto Expuesto | Red Interna |
|---|---|---|---|
| `eventos-uni-gateway` | Nginx API Gateway & Load Balancer | `http://localhost:8088` | `perimetro-net`, `backend-net` |
| `eventos-uni-app-1` | Nodo de Aplicación Backend 1 (Gunicorn) | Interno (`5000`) | `backend-net`, `db-net` |
| `eventos-uni-app-2` | Nodo de Aplicación Backend 2 (Gunicorn) | Interno (`5000`) | `backend-net`, `db-net` |
| `eventos-uni-redis` | Redis Cache & Sesiones Compartidas | Interno (`6379`) | `backend-net` |
| `eventos-uni-db-primary` | PostgreSQL 16 Primario (Write Master) | `localhost:5432` | `db-net` |
| `eventos-uni-db-replica` | PostgreSQL 16 Réplica (Read Replica) | `localhost:5433` | `db-net` |

👉 **Acceso a la Plataforma**: Ingrese mediante el Gateway perimetral en **`http://localhost:8088`**.

### 3. Desmontar y Detener el Clúster

Para detener todos los contenedores y liberar los recursos del sistema:

```bash
# Detener y remover los contenedores y redes
docker-compose down

# (Opcional) Detener y purgar también los volúmenes de datos persistentes
docker-compose down -v
```

---

## ☁️ Modo Producción en la Nube (Render + Supabase Clúster)

1. **Clúster Supabase (PostgreSQL 16)**:
   - `UNI-CLUSTER-PRIMARIO` (Escrituras) y `UNI-CLUSTER-REPLICA` (Lecturas).
2. **Persistencia de Imágenes (Supabase Storage)**:
   - Crear un Bucket público llamado **`eventos-portadas`** en el panel de Supabase -> Storage.
   - Copiar el `Project URL` y la `API Key` (anon o service_role).
3. **Servidor Web Render (PaaS)**:
   - Web Service en Python 3 conectado a la rama `Backend/Backend-Services`.
   - Start Command: `gunicorn --config gunicorn.conf.py app:app`
   - Variables de Entorno en Render:
     - `DATABASE_URL`: URI de Connection Pooling IPv4 (puerto 6543) de Supabase.
     - `DATABASE_READ_URL`: URI de réplica de lectura.
     - `SUPABASE_URL`: `https://[PROJECT-REF].supabase.co`
     - `SUPABASE_KEY`: Clave pública o de servicio de Supabase.
     - `SUPABASE_BUCKET`: `eventos-portadas`

---

## 🔒 Protocolo de Seguridad para el Equipo de Desarrollo

1. **Nunca modifiques ni subas archivos `.env` a GitHub**. El archivo `.gitignore` protege automáticamente `.env`, `.env.local` y bases de datos locales `*.db`.
2. **Usa siempre `.env.example`**: Cada ingeniero debe copiar `.env.example` a su propio `.env` local (`cp .env.example .env`).
3. **Las credenciales de producción de Supabase** solo existen en el panel privado de Render, permitiendo que el equipo trabaje en local de forma aislada y segura.

---

## 🔑 Credenciales de Acceso Institucional

| Rol | Correo / Identificador | Contraseña | Vista Principal | Permisos |
|---|---|---|---|---|
| **Encargado de Área** | `encargado@uni.edu.ni` | `admin123` | `/` (`index.html`) | Gestión de eventos de su unidad, creación de actividades y toma de asistencia. |
| **Rectoría / Dirección** | `rector@uni.edu.ni` | `rector123` | `/rector` (`rector.html`) | Supervisión nacional, métricas globales, eliminación de eventos y arbitraje de conflictos. |
| **Estudiante Padrón** | Carné: `2021-0001U` / Cédula: `001-030704-1067H` | N/A | Escaneo USB HID | Verificación en toma de asistencia. |
| **Docente Padrón** | Código: `EMP-9082` / Cédula: `001-150880-0002A` | N/A | Escaneo USB HID | Verificación en toma de asistencia. |

---

## 📡 Catálogo de Endpoints de la API RESTful

| Método | Endpoint | Blueprint | Autenticación | Descripción |
|---|---|---|---|---|
| `POST` | `/api/auth/login` | `auth_bp` | Pública | Login polimórfico (Email, Cédula, Carné, Código) con emisión de token HMAC. |
| `POST` | `/api/auth/logout` | `auth_bp` | Requerida | Cierre de sesión y purga de estado en servidor. |
| `GET` | `/api/auth/me` | `auth_bp` | Requerida | Consulta de usuario actual y renovación de token de sesión. |
| `GET` | `/api/eventos` | `eventos_bp` | Requerida | Lista de actividades institucionales con estado dinámico. |
| `POST` | `/api/eventos` | `eventos_bp` | Encargado / Rector | Creación transaccional de actividad con alineación estratégica 2026. |
| `PUT` | `/api/eventos/<id>` | `eventos_bp` | Encargado / Rector | Modificación de actividad (bloqueada para actividades finalizadas). |
| `DELETE`| `/api/eventos/<id>` | `eventos_bp` | Rector | Eliminación física (bloqueada si tiene asistentes o está activa). |
| `POST` | `/api/eventos/<id>/activar` | `eventos_bp` | Encargado / Rector | Transición manual de estado a 'activos'. |
| `POST` | `/api/eventos/<id>/finalizar`| `eventos_bp` | Encargado / Rector | Transición manual de estado a 'pasados'. |
| `POST` | `/api/asistencia/<id>` | `asistencia_bp` | Requerida | Registro atómico de asistencia (USB HID / Manual) con prevención de duplicados. |
| `POST` | `/api/asistencia/<id>/toggle-estado` | `asistencia_bp` | Requerida | Apertura / Cierre de asistencia sin alterar fechas del evento. |
| `GET` | `/api/asistencia/<id>` | `asistencia_bp` | Requerida | Listado aplanado de los 26 campos normalizados de asistentes. |
| `POST` | `/api/asistencia/persona-nueva` | `asistencia_bp` | Requerida | Alta rápida de persona en padrón 5FN + asistencia inmediata. |
| `GET` | `/api/catalogos` | `catalogos_bp` | Requerida | Servicio unificado de catálogos (Sedes, Tipos, Ejes, Líneas) con caché. |
| `GET` | `/api/stats/evento/<id>` | `stats_bp` | Requerida | Agregaciones demográficas 5FN en tiempo real por evento. |
| `GET` | `/api/stats/globales` | `stats_bp` | Requerida | Indicadores y métricas agregadas para el Dashboard de Rectoría. |
| `POST` | `/api/v1/sync` | `sync_bp` | Requerida / Hardware | Sincronización batch bidireccional (*Push & Pull*) con reconciliación UPSERT. |
| `GET` | `/api/v1/sync/status` | `sync_bp` | Requerida | Historial y telemetría de lotes de sincronización procesados. |
| `GET` | `/api/v1/sync/conflicts` | `sync_bp` | Encargado / Rector | Consulta de colisiones concurrentes pendientes de resolución. |
| `POST` | `/api/v1/sync/resolve` | `sync_bp` | Rector | Arbitraje manual de conflictos de sincronización. |
| `POST` | `/api/v1/sync/nodes/register` | `sync_bp` | Rector | Registro y autorización de nuevas terminales de campo (MAC / API Key). |
| `GET` | `/api/v1/sync/nodes` | `sync_bp` | Requerida | Listado de nodos de campo autorizados y estado de última conexión. |
| `POST` | `/api/uploads/image` | `uploads_bp` | Requerida | Carga validada de imágenes de portada (máx. 5 MB, formatos seguros). |
