---
name: validacion-academica
description: >-
  Instrucciones y procedimientos para auditar y verificar la elegibilidad institucional
  de estudiantes (CU-01, CU-09 y Fase 1). Úsese cuando se deba validar la matrícula activa,
  el avance en 4to o 5to año académico, o estructurar los antecedentes académicos del CV.
---

# Skill: Validación Académica y Elegibilidad Estudiantil

Esta skill proporciona las directrices y procedimientos técnicos para garantizar que únicamente los estudiantes universitarios que cumplan las normativas académicas institucionales puedan acceder y postularse a la bolsa de pasantías.

---

## 1. Reglas de Elegibilidad Institucional (CU-01 y CU-09)

Para que un estudiante sea clasificado como **Elegible para Pasantías**, el sistema debe verificar de forma atómica:
1.  **Matrícula Vigente**: Existe al menos un registro en `matriculas` con `estado == 'Activa'`.
2.  **Avance Académico Mínimo**: El campo `anio_academico` en la matrícula activa debe ser estrictamente `4` o `5`.
3.  **Carrera Universitaria**: El estudiante debe estar vinculado a una carrera registrada en el catálogo `carreras`.
4.  **Expediente Completo (CU-01)**:
    *   Dirección de residencia principal (`es_principal = True` en `direcciones_estudiante`).
    *   Teléfono de contacto principal (`es_principal = True` en `telefonos_estudiante`).
    *   Registro de educación secundaria/técnica previa en `educacion_previa_estudiante`.

---

## 2. Lógica de Verificación en Backend (Python / SQLAlchemy)

Al evaluar a un estudiante antes de permitir una postulación o al auditar desde el panel de vinculación:

```python
from models.perfil_estudiante import Estudiante, Matricula

def verificar_elegibilidad_estudiante(id_estudiante: int) -> dict:
    estudiante = Estudiante.query.get(id_estudiante)
    if not estudiante:
        return {"elegible": False, "motivo": "Estudiante no encontrado"}

    # Obtener última matrícula registrada
    matricula_activa = Matricula.query.filter_by(
        id_estudiante=id_estudiante,
        estado="Activa"
    ).order_by(Matricula.anio_academico.desc()).first()

    if not matricula_activa:
        return {
            "elegible": False,
            "motivo": "El estudiante no posee una matrícula académica activa."
        }

    if matricula_activa.anio_academico not in (4, 5):
        return {
            "elegible": False,
            "motivo": f"El estudiante está cursando el año {matricula_activa.anio_academico}. Las pasantías requieren estar en 4to o 5to año."
        }

    return {
        "elegible": True,
        "carrera_id": matricula_activa.id_carrera,
        "carrera_nombre": matricula_activa.carrera.nombre,
        "anio_academico": matricula_activa.anio_academico,
        "periodo": matricula_activa.periodo_academico,
    }
```

---

## 3. Acciones de Auditoría Institucional (CU-09)

*   Todo intento de postulación denegado por falta de matrícula activa o año inferior a 4to debe ser notificado al estudiante con un mensaje explicativo claro.
*   El Administrador de Vinculación puede auditar en cualquier momento la lista de postulantes filtrando por carrera y año académico.
