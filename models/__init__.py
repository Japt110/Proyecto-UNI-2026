"""
===============================================================================
SISTEMA WEB DE CONTROL DE PASANTÍAS - MODELOS ORM UNIFICADOS
===============================================================================
Exporta todos los modelos relacionales del sistema organizados por subdominio:
- Subdominio A: Catálogos (8 tablas)
- Subdominio B: Perfil Socio-Académico (5 tablas)
- Subdominio C: Actores Externos (3 tablas)
- Subdominio D: Experiencias - Prácticas y Pasantías (11 tablas)
- Subdominio E: Usuarios y Auditoría (3 tablas)
Total: 30 tablas en estricta conformidad con el diagrama relacional Mermaid.
===============================================================================
"""

from database import db

# Subdominio A: Catálogos
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

# Subdominio B: Perfil Socio-Académico
from models.perfil_estudiante import (
    Estudiante,
    DireccionEstudiante,
    TelefonoEstudiante,
    EducacionPreviaEstudiante,
    Matricula,
)

# Subdominio C: Actores Externos
from models.actores_externos import (
    EntidadReceptora,
    TutorDocente,
    SupervisorInstitucional,
)

# Subdominio D: Experiencias
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

# Subdominio E: Usuarios y Auditoría
from models.usuarios_auditoria import (
    Usuario,
    AuditoriaCambios,
    AuditoriaSesiones,
)

# Ofertas y Aplicaciones de Pasantías
from models.ofertas import (
    OfertaPasantia,
    AplicacionOferta,
)

__all__ = [
    "db",
    # Subdominio A
    "Pais",
    "Etnia",
    "Departamento",
    "Municipio",
    "CentroEducativo",
    "AreaCarrera",
    "Carrera",
    "Beca",
    # Subdominio B
    "Estudiante",
    "DireccionEstudiante",
    "TelefonoEstudiante",
    "EducacionPreviaEstudiante",
    "Matricula",
    # Subdominio C
    "EntidadReceptora",
    "TutorDocente",
    "SupervisorInstitucional",
    # Subdominio D
    "Experiencia",
    "Practica",
    "Pasantia",
    "AsignacionExperiencia",
    "PlanTrabajo",
    "ActividadPlan",
    "EntregablePlan",
    "HitoPlan",
    "CriterioEvaluacion",
    "Evaluacion",
    "Documento",
    # Subdominio E
    "Usuario",
    "AuditoriaCambios",
    "AuditoriaSesiones",
    # Ofertas y Aplicaciones
    "OfertaPasantia",
    "AplicacionOferta",
]