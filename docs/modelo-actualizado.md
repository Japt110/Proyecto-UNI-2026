# Modelo socioacadémico actualizado

Se adopta el modelo de 30 tablas de `Base de Datosup/Diagrama Entidad Relación/deepseek_mermaid_20261106_16d8f4.mermaid`, contrastado con `Script SQL.txt` y `Diagrama DBML.txt`. La fuente ejecutable mantenida en el proyecto es `models/schema.py`; el servidor no depende de Downloads. Se incorpora `usuarios.email VARCHAR(120) NOT NULL`, con unicidad sin distinguir mayúsculas, y no se incorpora ningún campo de carné. `usuarios.ruta_imagen` está disponible; esta migración no implementa la subida de fotografías.

Hay 30 tablas de dominio, más `auth_sessions` para sesiones revocables y `alembic_version` para controlar migraciones. `auditoria_sesiones` es un historial y no reemplaza las sesiones activas.

## Conversión de los datos existentes

La conversión soportada de la base anterior es SQLite. Detener el servidor y ejecutar desde la raíz del repositorio, indicando una carpeta privada para respaldos:

```powershell
python scripts/migrate_database.py --backup-dir C:\ruta\privada\respaldos
```

La herramienta usa `DATABASE_URL` o la base local configurada, crea una copia SQLite consistente, verifica su integridad y cuentas, ejecuta Alembic dentro de una transacción y comprueba claves foráneas, integridad, correos y hashes. Produce un informe JSON de conteos y correspondencias de identificadores. Los respaldos contienen datos personales y hashes: no se publican ni se versionan.

Se trasladan departamentos, ciudades a municipios, estudiantes con sus datos de identidad, ciudades de residencia conocidas, áreas, carreras, datos de matrícula disponibles y cuentas. Rector pasa a Administrador; Encargado a Coordinador; Asistencia a Consulta; Estudiante conserva su rol. El acceso por código y correo sigue funcionando. Los hashes de contraseñas se conservan y las sesiones previas se invalidan por el cambio de identificadores.

Los nombres históricos que no estaban separados se conservan completos en `nombre`, dejando `apellido` pendiente. No se adivina la separación. Los registros de trabajadores, eventos, asistencias, sedes, unidades, sincronización y bitácoras previas, así como los campos sin equivalente, permanecen íntegros en el respaldo. No se convierten eventos en experiencias ni trabajadores en tutores por suposición. Las antiguas rutas de eventos y sincronización dejan de registrarse: devuelven una respuesta controlada, no consultan tablas eliminadas. Sus archivos de código antiguos se conservan como referencia, pero no forman parte de la aplicación activa.

La lista de convocatorias y postulaciones que ya utilizaba almacenamiento del navegador mantiene ese comportamiento. Este cambio no añade entidades de convocatoria ni postulación ausentes en el modelo proporcionado.

## Adaptaciones necesarias del modelo

- `fecha_nacimiento`, `apellido` histórico, `dimension_nacional`, `id_pais_origen`, `estado_civil` e `hijos` pueden quedar pendientes. El registro actual no solicita esos datos. No se asume país, estado civil, hijos ni fecha de nacimiento a partir de la cédula.
- La dirección detallada y zona pueden quedar pendientes cuando únicamente se conoce el municipio. La duración de carrera, período, modalidad, año y turno de matrícula pueden quedar pendientes al trasladar información incompleta. Los demás campos y relaciones se conservan según el modelo. Las matrículas heredadas toman el estado predeterminado `Activa` del esquema; requieren revisión institucional si su vigencia real es diferente.
- `edad` se actualiza al escribir la fecha de nacimiento; la propiedad `edad_actual` y la vista `vw_perfil_estudiante` la calculan al consultar. Se evita la expresión generada del SQL original que depende de `CURRENT_DATE`: PostgreSQL exige funciones inmutables en columnas generadas. Fuente: https://www.postgresql.org/docs/current/ddl-generated-columns.html
- Se mantienen restricciones de roles, referencias, unicidad normalizada y asociaciones principales/activas. Los criterios se editan en borrador y deben sumar 100 al aprobar el plan; un plan aprobado bloquea cambios en sus criterios. Esta regla permite que SQLite y PostgreSQL tengan el mismo comportamiento sin triggers diferidos exclusivos de PostgreSQL.
- La auditoría usa la clave primaria real de cada tabla; no construye nombres inexistentes como `id_estudiantes` ni convierte números de transacción a UUID. Excluye `password_hash` de los datos anterior/nuevo. La vista pública de auditoría solo expone metadatos; no publica JSON con datos personales. El actor/contexto de auditoría de cambios puede ser nulo cuando la operación no lo aporta; los eventos de autenticación registran cuenta, IP y agente de usuario.
- El registro crea estudiante y cuenta de forma atómica, mantiene validación y CSRF, asigna Estudiante en el servidor y genera un nombre de usuario técnico. Los usuarios acceden por CUP, correo, cédula o nombre de usuario. El CUP admite hasta 20 caracteres según el nuevo esquema.
- El perfil ahora consulta únicamente los datos de la cuenta autenticada y se presenta en lectura. Se retiraron el carné y las acciones de demostración que anunciaban guardados o eliminaciones inexistentes. La edición y la carga de fotos siguen pendientes.

## Instalaciones nuevas y verificación

```sh
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m unittest discover -s tests -p "test_*.py" -v
node --test tests/auth-client.test.cjs tests/registration-validation.test.mjs
```

El servidor ya no crea tablas automáticamente ni oculta errores de esquema. Las pruebas crean bases SQLite aisladas. Se comprueba además la compilación del DDL para PostgreSQL, pero no se ha ejecutado la migración contra una instancia PostgreSQL en esta sesión. Una base PostgreSQL heredada necesita una conversión de datos específica y la herramienta la rechaza antes de modificarla. No se ha desplegado ni modificado ninguna base remota.

Para revertir la conversión local, detener la aplicación y restaurar el respaldo junto con el código anterior. No ejecutar semillas antiguas: recreaban y borraban datos del esquema de eventos.
