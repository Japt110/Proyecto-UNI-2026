---
name: metricas-vinculacion
description: >-
  Instrucciones y consultas analíticas para la generación de estadísticas y métricas del
  Gestor de Vinculación Universitario (CU-10). Úsese cuando se soliciten reportes sobre
  demanda de carreras, absorción de empresas o indicadores de éxito del programa de pasantías.
---

# Skill: Reportes y Métricas Institucionales de Vinculación

Esta skill proporciona las consultas relacionales y algoritmos de agregación estadística para responder a las necesidades de reporting del Gestor de Vinculación Universitario.

---

## 1. Indicadores Clave de Desempeño (KPIs)

El Gestor de Vinculación monitorea tres dimensiones críticas:
1.  **Demanda por Carrera**: Cuántas vacantes y postulaciones se concentran en cada programa académico.
2.  **Absorción de Talento por Empresa**: Cuántos estudiantes han sido contratados/aceptados por cada entidad receptora.
3.  **Tasa de Efectividad de Matching**: Porcentaje de postulaciones que avanzaron satisfactoriamente de `Postulado` a `Aceptado`.

---

## 2. Consultas Analíticas (SQL / SQLAlchemy)

### A. Demanda por Carrera Universitaria
Mide el número de vacantes y postulaciones generadas por carrera:

```python
from sqlalchemy import func
from database import db
from models.catalogos import Carrera
from models.ofertas import OfertaPasantia, AplicacionOferta
from models.perfil_estudiante import Matricula

def obtener_demanda_por_carrera():
    return db.session.query(
        Carrera.nombre.label("carrera"),
        func.count(OfertaPasantia.id_oferta).label("total_ofertas"),
        func.sum(OfertaPasantia.cupos).label("plazas_totales")
    ).outerjoin(OfertaPasantia, Carrera.id_carrera == OfertaPasantia.id_carrera)\
     .group_by(Carrera.id_carrera)\
     .order_by(func.count(OfertaPasantia.id_oferta).desc())\
     .all()
```

### B. Absorción de Talento por Entidad Receptora
Mide cuántos pasantes han sido aceptados formalmente por cada empresa:

```python
from models.actores_externos import EntidadReceptora
from models.ofertas import OfertaPasantia, AplicacionOferta

def obtener_absorcion_por_empresa():
    return db.session.query(
        EntidadReceptora.nombre.label("empresa"),
        EntidadReceptora.tipo.label("tipo_empresa"),
        func.count(AplicacionOferta.id_aplicacion).label("estudiantes_aceptados")
    ).join(OfertaPasantia, EntidadReceptora.id_entidad == OfertaPasantia.id_entidad)\
     .join(AplicacionOferta, OfertaPasantia.id_oferta == AplicacionOferta.id_oferta)\
     .filter(AplicacionOferta.estado == "Aceptada")\
     .group_by(EntidadReceptora.id_entidad)\
     .order_by(func.count(AplicacionOferta.id_aplicacion).desc())\
     .all()
```

### C. Embudo de Conversión de Postulaciones
Distribución de postulaciones en los estados del embudo:
`Postulado` ➔ `En_Revision` ➔ `Entrevista_Programada` ➔ `Aceptado` / `Rechazado`.

---

## 3. Formato de Salida para Dashboard
Los datos agregados deben entregarse con estructura JSON adecuada para widgets de gráficos (barras, torta y medidores de progreso) en las vistas del panel de administración.
