/**
 * ==============================================================================
 * PASANTÍAS UNI - CONTROLADOR PRINCIPAL Y DE ADMINISTRACIÓN
 * Gestiona: Vista Admin / Usuario, Postulación con CV (cualquier formato),
 * Panel de Candidatos, Aprobación / Rechazo, Exportación a CSV con BOM UTF-8,
 * Pestañas Activas vs Historial privado, y Sistema de Notificaciones.
 * ==============================================================================
 */

// Versión de los datos semilla — incrementar para forzar actualización limpia de caché
const DATA_VERSION = "v3-claudio-2026";

// 3 Pasantías reales de prueba
const DEFAULT_PASANTIAS = [
  {
    id: 1,
    titulo: "Pasantía en Desarrollo de Software",
    tipo: "Académica",
    modalidad: "Presencial",
    duracion: "160H",
    experiencia: "Sin experiencia",
    sector: "Tecnología",
    ciudad: "Managua",
    descripcion: "Prácticas profesionales en el área de ingeniería de software dentro del Departamento de Sistemas de la UNI. El pasante participará en el ciclo completo de desarrollo: levantamiento de requerimientos, diseño de arquitectura, implementación en Python/Django, pruebas unitarias e integración continua con GitHub Actions. Se requiere disponibilidad de lunes a viernes de 8:00 a.m. a 12:00 p.m. durante 4 meses calendario. El equipo supervisor asignará tareas semanales con retroalimentación directa del coordinador de área. Al finalizar se otorga carta de reconocimiento oficial firmada por la Dirección de Extensión Universitaria.",
    empresa: "Departamento de Sistemas — UNI",
    requisitos: "Cursando al menos el 4° año de Ingeniería en Computación o carrera afín. Conocimientos básicos de Python y SQL. Proactividad y trabajo en equipo.",
    beneficios: "Carta de recomendación, acceso a laboratorios especializados, mentoría técnica personalizada.",
    estado: "Activo"
  },
  {
    id: 2,
    titulo: "Pasantía en Análisis Estructural",
    tipo: "Profesional",
    modalidad: "Híbrida",
    duracion: "240H",
    experiencia: "Prácticas",
    sector: "Civil",
    ciudad: "Managua",
    descripcion: "Pasantía orientada a estudiantes avanzados de Ingeniería Civil con enfoque en análisis y diseño estructural. El pasante colaborará con el equipo técnico de la empresa en la elaboración de memorias de cálculo para estructuras de concreto reforzado, revisión de planos constructivos en AutoCAD y SAP2000, e inspección de obras en campo. Modalidad híbrida: 3 días presencial en oficina (zona Carretera Sur) y 2 días remoto. Se exige disponibilidad total de 6 meses.",
    empresa: "COPRECA S.A.",
    requisitos: "4° o 5° año de Ingeniería Civil. Manejo de AutoCAD y conocimiento básico de SAP2000. Carné universitario vigente.",
    beneficios: "Estipendio mensual de C$3,500, equipo de protección personal incluido, posibilidad de incorporación laboral al concluir.",
    estado: "Activo"
  },
  {
    id: 3,
    titulo: "Pasantía en Automatización Industrial",
    tipo: "Académica",
    modalidad: "Presencial",
    duracion: "320H",
    experiencia: "Junior",
    sector: "Industrial",
    ciudad: "León",
    descripcion: "Programa de pasantías en planta industrial para estudiantes de Ingeniería Electrónica o Mecatrónica. El pasante trabajará en el área de automatización y control de procesos, apoyando la programación de PLCs Allen-Bradley, configuración de HMIs y análisis de fallas en líneas de producción. La pasantía incluye capacitación inicial de 2 semanas en el uso de software Studio 5000. Jornada completa de lunes a viernes. Duración: 8 meses.",
    empresa: "Industrias León S.A. de C.V.",
    requisitos: "Cursando 4° o 5° año de Ingeniería Electrónica, Mecatrónica o Industrial. Conocimientos de lógica de control y circuitos eléctricos. Experiencia previa en laboratorio es un plus.",
    beneficios: "Estipendio mensual de C$5,000, transporte interno en planta, seguro contra accidentes, carta de pasantía con evaluación de desempeño.",
    estado: "Activo"
  }
];

// Candidatos de prueba iniciales para que el Administrador pueda visualizar y exportar de inmediato
const DEFAULT_SOLICITUDES = [
  {
    id: "sol-101",
    pasantiaId: 1,
    pasantiaTitulo: "Pasantía en Desarrollo de Software",
    nombre: "Juan Alejandro Pérez",
    email: "juan.perez@est.uni.edu.ni",
    telefono: "+505 8734-1122",
    carrera: "Ing. en Computación - 4to Año",
    cvFileName: "CV_Juan_Alejandro_Perez.pdf",
    cvFileType: "application/pdf",
    cvFileSize: "420 KB",
    cvFileData: null,
    fechaSolicitud: "2026-10-25T14:30:00",
    mensaje: "Poseo experiencia en desarrollo backend con Python y bases de datos SQL.",
    estado: "pendiente"
  },
  {
    id: "sol-102",
    pasantiaId: 1,
    pasantiaTitulo: "Pasantía en Desarrollo de Software",
    nombre: "María Fernanda López",
    email: "maria.lopez@est.uni.edu.ni",
    telefono: "+505 8421-9988",
    carrera: "Ing. en Sistemas - 5to Año",
    cvFileName: "Curriculum_Maria_Lopez.docx",
    cvFileType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    cvFileSize: "850 KB",
    cvFileData: null,
    fechaSolicitud: "2026-10-26T09:15:00",
    mensaje: "Interés en proyectos de extensión universitaria y desarrollo de APIs REST.",
    estado: "aceptado"
  },
  {
    id: "sol-103",
    pasantiaId: 2,
    pasantiaTitulo: "Pasantía en Análisis Estructural",
    nombre: "Carlos Eduardo Ruiz",
    email: "carlos.ruiz@est.uni.edu.ni",
    telefono: "+505 8655-4321",
    carrera: "Ing. Civil - 4to Año",
    cvFileName: "CV_Carlos_Ruiz_Civil.pdf",
    cvFileType: "application/pdf",
    cvFileSize: "1.1 MB",
    cvFileData: null,
    fechaSolicitud: "2026-10-27T11:00:00",
    mensaje: "Manejo intermedio de AutoCAD y SAP2000.",
    estado: "pendiente"
  }
];

// Notificaciones iniciales de prueba
const DEFAULT_NOTIFICACIONES = [
  {
    id: "notif-1",
    tipo: "bienvenida",
    titulo: "Bienvenido al Sistema de Pasantías UNI",
    mensaje: "Explora las convocatorias abiertas, guarda tus favoritas y postúlate adjuntando tu CV en el formato que desees.",
    pasantiaId: null,
    fecha: new Date(Date.now() - 3600000 * 4).toISOString(),
    leida: false
  }
];

class PasantiasApp {
  constructor() {
    this.checkDataVersion();
    this.pasantias = this.loadPasantias();
    this.solicitudes = this.loadSolicitudes();
    this.notificaciones = this.loadNotificaciones();
    this.guardadas = this.loadGuardadas(); // Set de IDs de pasantías favoritas

    this.currentRole = this.getInitialRole(); // 'admin' | 'usuario'
    this.currentTab = 'activo'; // 'activo' | 'historial'

    // Estado del modal de postulación
    this.activeSolPasantia = null;
    this.tempCVFile = null;

    // Estado del modal de candidatos (Admin)
    this.activeCandPasantia = null;
    this.candFilterState = 'todos';
    this.candSearchQuery = '';

    this.filters = {
      search: "",
      experiencia: "",
      modalidad: "",
      sector: "",
      ciudad: ""
    };

    this.init();
  }

  checkDataVersion() {
    try {
      const storedVersion = localStorage.getItem("uni_pasantias_version");
      if (storedVersion !== DATA_VERSION) {
        localStorage.removeItem("uni_pasantias_data");
        localStorage.removeItem("uni_solicitudes_data");
        localStorage.removeItem("uni_notificaciones_data");
        localStorage.setItem("uni_pasantias_version", DATA_VERSION);
      }
    } catch (_) {}
  }

  loadPasantias() {
    try {
      const stored = localStorage.getItem("uni_pasantias_data");
      if (stored) return JSON.parse(stored);
    } catch (_) {}
    return JSON.parse(JSON.stringify(DEFAULT_PASANTIAS));
  }

  savePasantias() {
    try {
      localStorage.setItem("uni_pasantias_data", JSON.stringify(this.pasantias));
    } catch (_) {}
  }

  loadSolicitudes() {
    try {
      const stored = localStorage.getItem("uni_solicitudes_data");
      if (stored) return JSON.parse(stored);
    } catch (_) {}
    return JSON.parse(JSON.stringify(DEFAULT_SOLICITUDES));
  }

  saveSolicitudes() {
    try {
      localStorage.setItem("uni_solicitudes_data", JSON.stringify(this.solicitudes));
    } catch (_) {}
  }

  loadNotificaciones() {
    try {
      const stored = localStorage.getItem("uni_notificaciones_data");
      if (stored) return JSON.parse(stored);
    } catch (_) {}
    return JSON.parse(JSON.stringify(DEFAULT_NOTIFICACIONES));
  }

  saveNotificaciones() {
    try {
      localStorage.setItem("uni_notificaciones_data", JSON.stringify(this.notificaciones));
    } catch (_) {}
  }

  loadGuardadas() {
    try {
      const stored = localStorage.getItem("uni_guardadas_data");
      if (stored) return new Set(JSON.parse(stored));
    } catch (_) {}
    return new Set();
  }

  saveGuardadas() {
    try {
      localStorage.setItem("uni_guardadas_data", JSON.stringify([...this.guardadas]));
    } catch (_) {}
  }

  getInitialRole() {
    const urlParams = new URLSearchParams(window.location.search);
    const roleParam = urlParams.get("role");
    if (roleParam === "admin" || roleParam === "usuario") {
      localStorage.setItem("uni_current_view_role", roleParam);
      return roleParam;
    }
    const savedRole = localStorage.getItem("uni_current_view_role");
    return savedRole === "usuario" ? "usuario" : "admin";
  }

  init() {
    document.addEventListener("DOMContentLoaded", () => {
      this.bindElements();
      this.bindEvents();
      this.applyRole(this.currentRole);
      this.updateTabCounts();
      this.renderGrid();
      this.renderNotificaciones();
      this.updateNotifBadge();
      this.initLucideIcons();
    });
  }

  bindElements() {
    this.pageWrapper = document.getElementById("pasantias-wrapper");
    this.gridContainer = document.getElementById("pasantias-grid");
    this.searchInput = document.getElementById("pasantias-search-input");
    this.roleIndicatorBadge = document.getElementById("role-indicator-badge");
    this.btnAgregarPasantia = document.getElementById("btn-agregar-pasantia");

    // Topbar & Drawer
    this.btnNotifTrigger = document.getElementById("btn-notif-trigger");
    this.notifBadgeCount = document.getElementById("notif-badge-count");
    this.btnProfileTrigger = document.getElementById("btn-profile-trigger");
    this.drawerPanel = document.getElementById("uni-drawer-panel");
    this.drawerBackdrop = document.getElementById("uni-drawer-backdrop");
    this.btnDrawerCollapse = document.getElementById("btn-drawer-collapse");
    this.btnDrawerLogout = document.getElementById("btn-drawer-logout");
    this.drawerNotifsList = document.getElementById("drawer-notifications-list");
    this.btnClearAllNotifs = document.getElementById("btn-clear-all-notifs");

    // Tabs
    this.tabBtnActivas = document.getElementById("tab-btn-activas");
    this.tabBtnHistorial = document.getElementById("tab-btn-historial");
    this.countActivas = document.getElementById("count-activas");
    this.countHistorial = document.getElementById("count-historial");
    this.tabSubtitleText = document.getElementById("tab-subtitle-text");

    // Modal Crear Pasantía
    this.modalOverlay = document.getElementById("modal-agregar-pasantia");
    this.btnCloseModal = document.getElementById("btn-close-modal");
    this.btnCancelModal = document.getElementById("btn-cancel-modal");
    this.formAgregarPasantia = document.getElementById("form-agregar-pasantia");

    // Modal Postulación (CV)
    this.modalSolicitud = document.getElementById("modal-solicitar-pasantia");
    this.btnCloseSolicitudModal = document.getElementById("btn-close-solicitud-modal");
    this.btnCancelSolicitud = document.getElementById("btn-cancel-solicitud");
    this.formSolicitarPasantia = document.getElementById("form-solicitar-pasantia");
    this.solicitudModalTitle = document.getElementById("solicitud-modal-title");
    this.solicitudPasantiaSubtitle = document.getElementById("solicitud-pasantia-subtitle");
    this.solicitudPasantiaIdInput = document.getElementById("solicitud-pasantia-id");
    this.cvDropzone = document.getElementById("cv-dropzone");
    this.solicitudCvFileInput = document.getElementById("solicitud-cv-file");
    this.cvDropzonePrompt = document.getElementById("cv-dropzone-prompt");
    this.cvSelectedPreview = document.getElementById("cv-selected-preview");
    this.cvPreviewName = document.getElementById("cv-preview-name");
    this.cvPreviewSize = document.getElementById("cv-preview-size");
    this.cvPreviewIcon = document.getElementById("cv-preview-icon");
    this.btnRemoveCV = document.getElementById("btn-remove-cv");

    // Modal Candidatos (Admin)
    this.modalCandidatos = document.getElementById("modal-candidatos-admin");
    this.btnCloseCandidatosModal = document.getElementById("btn-close-candidatos-modal");
    this.btnCandidatosModalClose = document.getElementById("btn-candidatos-modal-close");
    this.candidatosModalTitle = document.getElementById("candidatos-modal-title");
    this.candidatosModalCompany = document.getElementById("candidatos-modal-company");
    this.candidatosPasantiaStatusBadge = document.getElementById("candidatos-pasantia-status-badge");
    this.candidatosTableTbody = document.getElementById("candidatos-table-tbody");
    this.candidatosEmptyState = document.getElementById("candidatos-empty-state");
    this.candidatosFooterInfo = document.getElementById("candidatos-footer-info");
    this.candidatosSearchInput = document.getElementById("candidatos-search-input");
    this.btnExportarCsv = document.getElementById("btn-exportar-csv");
    this.btnExportarCsvFooter = document.getElementById("btn-exportar-csv-footer");

    // Stats elements
    this.statCountTotal = document.getElementById("stat-count-total");
    this.statCountPendientes = document.getElementById("stat-count-pendientes");
    this.statCountAceptados = document.getElementById("stat-count-aceptados");
    this.statCountRechazados = document.getElementById("stat-count-rechazados");
  }

  bindEvents() {
    // 1. Drawer & Notificaciones
    if (this.btnProfileTrigger) {
      this.btnProfileTrigger.addEventListener("click", (e) => {
        e.stopPropagation();
        this.openDrawer();
      });
    }
    if (this.btnNotifTrigger) {
      this.btnNotifTrigger.addEventListener("click", (e) => {
        e.stopPropagation();
        this.openDrawer();
      });
    }
    if (this.btnDrawerCollapse) {
      this.btnDrawerCollapse.addEventListener("click", () => this.closeDrawer());
    }
    if (this.drawerBackdrop) {
      this.drawerBackdrop.addEventListener("click", () => this.closeDrawer());
    }
    if (this.btnClearAllNotifs) {
      this.btnClearAllNotifs.addEventListener("click", () => this.clearAllNotificaciones());
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.closeDrawer();
        this.closeModal();
        this.closeSolicitudModal();
        this.closeCandidatosModal();
      }
    });

    // 2. Búsqueda en tiempo real de pasantías
    if (this.searchInput) {
      this.searchInput.addEventListener("input", (e) => {
        this.filters.search = e.target.value.toLowerCase().trim();
        this.renderGrid();
      });
    }

    // 3. Dropdowns de Filtros
    this.initFilterDropdowns();

    // 4. Tabs Activas / Historial
    if (this.tabBtnActivas) {
      this.tabBtnActivas.addEventListener("click", () => this.switchTab('activo'));
    }
    if (this.tabBtnHistorial) {
      this.tabBtnHistorial.addEventListener("click", () => this.switchTab('historial'));
    }

    // 5. Modal Agregar Pasantía (Admin)
    if (this.btnAgregarPasantia) {
      this.btnAgregarPasantia.addEventListener("click", () => this.openModal());
    }
    if (this.btnCloseModal) {
      this.btnCloseModal.addEventListener("click", () => this.closeModal());
    }
    if (this.btnCancelModal) {
      this.btnCancelModal.addEventListener("click", () => this.closeModal());
    }
    if (this.formAgregarPasantia) {
      this.formAgregarPasantia.addEventListener("submit", (e) => this.handleCreatePasantia(e));
    }

    // 6. Modal Solicitud / CV
    if (this.btnCloseSolicitudModal) {
      this.btnCloseSolicitudModal.addEventListener("click", () => this.closeSolicitudModal());
    }
    if (this.btnCancelSolicitud) {
      this.btnCancelSolicitud.addEventListener("click", () => this.closeSolicitudModal());
    }
    if (this.formSolicitarPasantia) {
      this.formSolicitarPasantia.addEventListener("submit", (e) => this.handleSolicitudSubmit(e));
    }
    if (this.btnRemoveCV) {
      this.btnRemoveCV.addEventListener("click", (e) => {
        e.stopPropagation();
        this.removeSelectedCV();
      });
    }
    this.initCVDropzone();

    // 7. Modal Candidatos (Admin)
    if (this.btnCloseCandidatosModal) {
      this.btnCloseCandidatosModal.addEventListener("click", () => this.closeCandidatosModal());
    }
    if (this.btnCandidatosModalClose) {
      this.btnCandidatosModalClose.addEventListener("click", () => this.closeCandidatosModal());
    }
    if (this.btnExportarCsv) {
      this.btnExportarCsv.addEventListener("click", () => this.exportarCandidatosCSV());
    }
    if (this.btnExportarCsvFooter) {
      this.btnExportarCsvFooter.addEventListener("click", () => this.exportarCandidatosCSV());
    }
    if (this.candidatosSearchInput) {
      this.candidatosSearchInput.addEventListener("input", (e) => {
        this.candSearchQuery = e.target.value.toLowerCase().trim();
        this.renderCandidatosTable();
      });
    }

    // Filtros por estado dentro del modal de candidatos
    document.querySelectorAll(".btn-cand-filter").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".btn-cand-filter").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.candFilterState = btn.dataset.filter || 'todos';
        this.renderCandidatosTable();
      });
    });

    // 8. Selector de Rol en el Drawer
    document.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-set-role]");
      if (btn) {
        const newRole = btn.dataset.setRole;
        this.setRole(newRole);
        this.closeDrawer();
      }
    });

    // 9. Cerrar Sesión
    if (this.btnDrawerLogout) {
      this.btnDrawerLogout.addEventListener("click", (e) => {
        e.preventDefault();
        window.location.href = "/login";
      });
    }
  }

  // --------------------------------------------------------------------------
  // CONTROL DE ROLES & TABS
  // --------------------------------------------------------------------------
  setRole(role) {
    this.currentRole = role;
    localStorage.setItem("uni_current_view_role", role);
    this.applyRole(role);

    // Si pasa a rol usuario y estaba en Historial (privado), volver a Activo
    if (role === 'usuario' && this.currentTab === 'historial') {
      this.switchTab('activo');
    }

    this.updateTabCounts();
    this.renderGrid();
    this.showToast(`Vista cambiada: ${role === 'admin' ? 'Administrador' : 'Usuario'}`, "info");
  }

  applyRole(role) {
    const isAdmin = role === "admin";
    if (isAdmin) {
      this.pageWrapper?.classList.remove("view-usuario-mode");
      this.pageWrapper?.classList.add("view-admin-mode");
    } else {
      this.pageWrapper?.classList.remove("view-admin-mode");
      this.pageWrapper?.classList.add("view-usuario-mode");
    }

    // Mostrar / Ocultar botón Agregar Pasantía
    if (this.btnAgregarPasantia) {
      this.btnAgregarPasantia.style.display = isAdmin ? 'block' : 'none';
    }

    // Mostrar / Ocultar Tab Historial (Solo Admin)
    if (this.tabBtnHistorial) {
      this.tabBtnHistorial.style.display = isAdmin ? 'inline-flex' : 'none';
    }

    this.updateRoleIndicator(role);
    this.updateDrawerRoleButtons(role);
  }

  updateRoleIndicator(role) {
    if (!this.roleIndicatorBadge) return;
    const isAdmin = role === 'admin';
    this.roleIndicatorBadge.textContent = isAdmin ? 'Administrador' : 'Usuario';
    this.roleIndicatorBadge.className = 'role-indicator-badge ' + (isAdmin ? 'role-admin' : 'role-usuario');
  }

  updateDrawerRoleButtons(role) {
    const adminBtn = document.querySelector('[data-set-role="admin"]');
    const usuarioBtn = document.querySelector('[data-set-role="usuario"]');
    if (adminBtn) adminBtn.classList.toggle('role-btn-active', role === 'admin');
    if (usuarioBtn) usuarioBtn.classList.toggle('role-btn-active', role === 'usuario');
  }

  switchTab(tab) {
    this.currentTab = tab;
    if (this.tabBtnActivas) {
      this.tabBtnActivas.classList.toggle('active', tab === 'activo');
    }
    if (this.tabBtnHistorial) {
      this.tabBtnHistorial.classList.toggle('active', tab === 'historial');
    }

    if (this.tabSubtitleText) {
      this.tabSubtitleText.textContent = tab === 'activo'
        ? "Pasantías vigentes disponibles para postulación"
        : "Historial de pasantías finalizadas (Archivo privado de administración)";
    }

    this.renderGrid();
  }

  updateTabCounts() {
    const activas = this.pasantias.filter(p => p.estado !== "Finalizado").length;
    const historial = this.pasantias.filter(p => p.estado === "Finalizado").length;

    if (this.countActivas) this.countActivas.textContent = activas;
    if (this.countHistorial) this.countHistorial.textContent = historial;
  }

  // --------------------------------------------------------------------------
  // RENDERIZADO DEL GRID DE PASANTÍAS
  // --------------------------------------------------------------------------
  renderGrid() {
    if (!this.gridContainer) return;
    const role = this.currentRole;
    const tab = this.currentTab;

    // 1. Filtrar por estado de la pestaña (Activo vs Historial)
    let list = this.pasantias.filter(p => {
      const isFinalizada = p.estado === "Finalizado";
      if (tab === 'activo') return !isFinalizada;
      return isFinalizada;
    });

    // Si es usuario regular, nunca mostrar finalizadas
    if (role === 'usuario') {
      list = list.filter(p => p.estado !== "Finalizado");
    }

    // 2. Filtrar por texto y dropdowns
    const filtered = list.filter(p => {
      if (this.filters.search) {
        const query = this.filters.search;
        const matchesText = p.titulo.toLowerCase().includes(query) ||
                            p.descripcion.toLowerCase().includes(query) ||
                            p.sector.toLowerCase().includes(query) ||
                            p.ciudad.toLowerCase().includes(query) ||
                            (p.empresa && p.empresa.toLowerCase().includes(query));
        if (!matchesText) return false;
      }
      if (this.filters.experiencia && p.experiencia.toLowerCase() !== this.filters.experiencia.toLowerCase()) return false;
      if (this.filters.modalidad  && p.modalidad.toLowerCase()  !== this.filters.modalidad.toLowerCase())  return false;
      if (this.filters.sector     && p.sector.toLowerCase()     !== this.filters.sector.toLowerCase())     return false;
      if (this.filters.ciudad     && p.ciudad.toLowerCase()     !== this.filters.ciudad.toLowerCase())     return false;
      return true;
    });

    this.updateTabCounts();

    if (filtered.length === 0) {
      const emptyMsg = tab === 'historial'
        ? "No hay pasantías archivadas en el historial."
        : "No se encontraron pasantías con los filtros seleccionados.";

      this.gridContainer.innerHTML = `
        <div class="pasantias-empty-grid">
          <i data-lucide="${tab === 'historial' ? 'archive' : 'inbox'}" class="empty-grid-icon"></i>
          <h4>${emptyMsg}</h4>
          <p>${tab === 'historial' ? 'Las pasantías que finalices aparecerán aquí de forma privada.' : 'Prueba cambiando tus términos de búsqueda o filtros.'}</p>
        </div>
      `;
      this.initLucideIcons();
      return;
    }

    this.gridContainer.innerHTML = filtered.map(p => {
      const candCount = this.solicitudes.filter(s => s.pasantiaId === p.id).length;
      const yaPostulo = this.yaPostulo(p.id);
      const isGuardada = this.guardadas.has(p.id);
      const isFinalizada = p.estado === "Finalizado";

      // Botones para Administrador
      const adminButtons = `
        <button type="button" class="btn-pasantia-candidatos" onclick="event.stopPropagation(); window.pasantiasApp.openCandidatosModal(${p.id})">
          <i data-lucide="users"></i> CANDIDATOS (${candCount})
        </button>
        ${!isFinalizada ? `
          <button type="button" class="btn-pasantia-terminar" onclick="event.stopPropagation(); window.pasantiasApp.terminarPeriodo(${p.id})">
            TERMINAR
          </button>
        ` : `
          <button type="button" class="btn-pasantia-reabrir" onclick="event.stopPropagation(); window.pasantiasApp.reabrirPeriodo(${p.id})">
            <i data-lucide="rotate-ccw"></i> REABRIR
          </button>
        `}
      `;

      // Botones para Usuario
      const userButtons = `
        <button type="button" class="btn-pasantia-guardar ${isGuardada ? 'is-guardada' : ''}" onclick="event.stopPropagation(); window.pasantiasApp.toggleGuardarPasantia(${p.id})">
          <i data-lucide="${isGuardada ? 'bookmark-check' : 'bookmark'}"></i> ${isGuardada ? 'GUARDADA' : 'GUARDAR'}
        </button>
        ${yaPostulo ? `
          <button type="button" class="btn-pasantia-solicitar btn-ya-postulado" disabled title="Ya has enviado tu solicitud">
            <i data-lucide="check"></i> POSTULADO
          </button>
        ` : `
          <button type="button" class="btn-pasantia-solicitar" onclick="event.stopPropagation(); window.pasantiasApp.openSolicitudModal(${p.id})">
            SOLICITAR
          </button>
        `}
      `;

      const actionButtons = role === 'admin' ? adminButtons : userButtons;

      const badgeModalidadClass = p.modalidad === 'Presencial' ? 'badge-presencial'
                                 : p.modalidad === 'Virtual'   ? 'badge-virtual'
                                 : 'badge-hibrida';

      return `
        <div class="pasantia-card ${isFinalizada ? 'pasantia-card-finalizada' : ''}" data-id="${p.id}" id="pasantia-card-${p.id}">
          <div class="pasantia-card-banner-wrapper">
            <img src="/static/img/pasantia_banner.jpg" alt="Pasantía UNI" class="pasantia-card-banner" />
            ${isFinalizada ? `<span class="card-status-overlay-badge"><i data-lucide="lock"></i> Período Finalizado</span>` : ''}
          </div>
          <div class="pasantia-card-body">
            <!-- Vista colapsada (vista rápida) -->
            <div class="pasantia-card-collapsed">
              <h3 class="pasantia-card-title">${p.titulo}</h3>
              <span class="pasantia-card-desc-label">Descripción:</span>
              <p class="pasantia-card-desc-preview">${p.descripcion}</p>
            </div>

            <!-- Vista expandida (al pasar el cursor) -->
            <div class="pasantia-card-expanded">
              <h3 class="pasantia-card-title">${p.titulo}</h3>
              <div class="pasantia-badges-row">
                <span class="pasantia-badge">${p.tipo}</span>
                <span class="pasantia-badge ${badgeModalidadClass}">${p.modalidad}</span>
                <span class="pasantia-badge">${p.duracion}</span>
              </div>
              ${p.empresa ? `<p class="pasantia-empresa"><i data-lucide="building-2"></i> ${p.empresa}</p>` : ''}
              
              <div class="pasantia-expanded-scroll">
                <span class="pasantia-card-desc-label">Descripción:</span>
                <p class="pasantia-card-desc-full">${p.descripcion}</p>
                ${p.requisitos ? `<span class="pasantia-card-desc-label" style="margin-top:10px;display:block;">Requisitos:</span><p class="pasantia-card-desc-full">${p.requisitos}</p>` : ''}
                ${p.beneficios ? `<span class="pasantia-card-desc-label" style="margin-top:10px;display:block;">Beneficios:</span><p class="pasantia-card-desc-full">${p.beneficios}</p>` : ''}
              </div>

              <div class="pasantia-actions-row">
                ${actionButtons}
              </div>
            </div>
          </div>
        </div>
      `;
    }).join("");

    this.initLucideIcons();
  }

  yaPostulo(pasantiaId) {
    return this.solicitudes.some(s => s.pasantiaId === pasantiaId && s.nombre === "Juan Alejandro Pérez");
  }

  // --------------------------------------------------------------------------
  // FINALIZAR PERÍODO (TERMINAR) & NOTIFICACIONES
  // --------------------------------------------------------------------------
  terminarPeriodo(id) {
    const item = this.pasantias.find(p => p.id === id);
    if (!item) return;

    if (!confirm(`¿Deseas finalizar el período de registro para "${item.titulo}"?\n\nLa pasantía dejará de proyectarse públicamente a los estudiantes y se archivará de manera privada en el Historial.`)) {
      return;
    }

    item.estado = "Finalizado";
    this.savePasantias();

    // 1. Notificar a todos los postulantes de esta pasantía
    const candidatosAfectados = this.solicitudes.filter(s => s.pasantiaId === id);
    this.addNotificacion(
      "pasantia_finalizada",
      "Período de pasantía finalizado",
      `El período de registro para "${item.titulo}" ha culminado. Tu postulación permanece registrada en evaluación.`,
      id
    );

    // 2. Notificar si el usuario la tenía guardada
    if (this.guardadas.has(id)) {
      this.addNotificacion(
        "favorito_finalizado",
        "Pasantía guardada finalizada",
        `La pasantía "${item.titulo}" que guardaste en tus favoritos ha finalizado su período de registro.`,
        id
      );
    }

    this.updateTabCounts();
    this.renderGrid();
    this.showToast(`Período finalizado. "${item.titulo}" se movió al Historial privado.`, "info");
  }

  reabrirPeriodo(id) {
    const item = this.pasantias.find(p => p.id === id);
    if (!item) return;

    item.estado = "Activo";
    this.savePasantias();
    this.updateTabCounts();
    this.renderGrid();
    this.showToast(`Pasantía "${item.titulo}" reactivada para postulación pública.`, "success");
  }

  toggleGuardarPasantia(id) {
    const item = this.pasantias.find(p => p.id === id);
    if (!item) return;

    if (this.guardadas.has(id)) {
      this.guardadas.delete(id);
      this.saveGuardadas();
      this.renderGrid();
      this.showToast(`Pasantía quitada de tus favoritos`, "info");
    } else {
      this.guardadas.add(id);
      this.saveGuardadas();
      this.renderGrid();
      this.showToast(`¡Pasantía guardada en tus favoritos! Te avisaremos si finaliza`, "success");
    }
  }

  // --------------------------------------------------------------------------
  // MODAL DE POSTULACIÓN CON CARGA DE CV (CUALQUIER FORMATO)
  // --------------------------------------------------------------------------
  openSolicitudModal(id) {
    const item = this.pasantias.find(p => p.id === id);
    if (!item) return;

    this.activeSolPasantia = item;
    if (this.solicitudModalTitle) this.solicitudModalTitle.textContent = "Postulación a Pasantía";
    if (this.solicitudPasantiaSubtitle) this.solicitudPasantiaSubtitle.textContent = item.titulo;
    if (this.solicitudPasantiaIdInput) this.solicitudPasantiaIdInput.value = item.id;

    // Resetear formulario
    if (this.formSolicitarPasantia) {
      this.formSolicitarPasantia.reset();
      const nombreInput = document.getElementById("solicitud-nombre");
      const emailInput = document.getElementById("solicitud-email");
      const telInput = document.getElementById("solicitud-telefono");
      const carreraInput = document.getElementById("solicitud-carrera");

      if (nombreInput) nombreInput.value = "Juan Alejandro Pérez";
      if (emailInput) emailInput.value = "juan.alejandro@uni.edu.ni";
      if (telInput) telInput.value = "+505 8899-7711";
      if (carreraInput) carreraInput.value = "Ingeniería en Computación - 4to Año";
    }

    this.removeSelectedCV();
    this.modalSolicitud?.classList.add("is-visible");
  }

  closeSolicitudModal() {
    this.modalSolicitud?.classList.remove("is-visible");
    this.activeSolPasantia = null;
    this.tempCVFile = null;
  }

  initCVDropzone() {
    if (!this.cvDropzone || !this.solicitudCvFileInput) return;

    // Click para abrir selector de archivos
    this.cvDropzone.addEventListener("click", () => {
      this.solicitudCvFileInput.click();
    });

    this.solicitudCvFileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        this.handleCVFileSelected(e.target.files[0]);
      }
    });

    // Drag & Drop
    ['dragenter', 'dragover'].forEach(eventName => {
      this.cvDropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.cvDropzone.classList.add('drag-over');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      this.cvDropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.cvDropzone.classList.remove('drag-over');
      });
    });

    this.cvDropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        this.handleCVFileSelected(e.dataTransfer.files[0]);
      }
    });
  }

  handleCVFileSelected(file) {
    if (!file) return;

    const formattedSize = this.formatFileSize(file.size);
    const fileName = file.name;
    const fileType = file.type || "application/octet-stream";

    // Leer como base64 para permitir posterior descarga por parte del admin
    const reader = new FileReader();
    reader.onload = (e) => {
      this.tempCVFile = {
        name: fileName,
        type: fileType,
        size: formattedSize,
        sizeBytes: file.size,
        data: e.target.result
      };

      // Actualizar UI del dropzone
      if (this.cvDropzonePrompt) this.cvDropzonePrompt.style.display = 'none';
      if (this.cvSelectedPreview) this.cvSelectedPreview.style.display = 'flex';
      if (this.cvPreviewName) this.cvPreviewName.textContent = fileName;
      if (this.cvPreviewSize) this.cvPreviewSize.textContent = formattedSize;

      this.initLucideIcons();
    };

    reader.onerror = () => {
      this.showToast("No se pudo leer el archivo seleccionado.", "error");
    };

    reader.readAsDataURL(file);
  }

  removeSelectedCV() {
    this.tempCVFile = null;
    if (this.solicitudCvFileInput) this.solicitudCvFileInput.value = "";
    if (this.cvDropzonePrompt) this.cvDropzonePrompt.style.display = 'flex';
    if (this.cvSelectedPreview) this.cvSelectedPreview.style.display = 'none';
  }

  formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  handleSolicitudSubmit(e) {
    e.preventDefault();
    if (!this.activeSolPasantia) return;

    if (!this.tempCVFile) {
      this.showToast("Por favor adjunta tu Currículum Vitae (CV) antes de enviar.", "error");
      return;
    }

    const nombre = document.getElementById("solicitud-nombre")?.value.trim() || "Estudiante UNI";
    const email = document.getElementById("solicitud-email")?.value.trim() || "estudiante@uni.edu.ni";
    const telefono = document.getElementById("solicitud-telefono")?.value.trim() || "+505 0000-0000";
    const carrera = document.getElementById("solicitud-carrera")?.value.trim() || "Ingeniería UNI";
    const mensaje = document.getElementById("solicitud-mensaje")?.value.trim() || "";

    const nuevaSolicitud = {
      id: "sol-" + Date.now(),
      pasantiaId: this.activeSolPasantia.id,
      pasantiaTitulo: this.activeSolPasantia.titulo,
      nombre,
      email,
      telefono,
      carrera,
      cvFileName: this.tempCVFile.name,
      cvFileType: this.tempCVFile.type,
      cvFileSize: this.tempCVFile.size,
      cvFileData: this.tempCVFile.data,
      fechaSolicitud: new Date().toISOString(),
      mensaje,
      estado: "pendiente"
    };

    this.solicitudes.unshift(nuevaSolicitud);
    this.saveSolicitudes();

    // Notificación en el Drawer para el usuario
    this.addNotificacion(
      "solicitud_enviada",
      "Solicitud Registrada",
      `Te has postulado con éxito a "${this.activeSolPasantia.titulo}". Tu CV (${this.tempCVFile.name}) está en revisión.`,
      this.activeSolPasantia.id
    );

    this.closeSolicitudModal();
    this.renderGrid();
    this.showToast(`¡Tu solicitud con CV para "${this.activeSolPasantia.titulo}" fue enviada exitosamente!`, "success");
  }

  // --------------------------------------------------------------------------
  // PANEL ADMINISTRADOR DE CANDIDATOS (ACEPTAR / RECHAZAR & EXPORTAR)
  // --------------------------------------------------------------------------
  openCandidatosModal(pasantiaId) {
    const item = this.pasantias.find(p => p.id === pasantiaId);
    if (!item) return;

    this.activeCandPasantia = item;
    this.candFilterState = 'todos';
    this.candSearchQuery = '';

    if (this.candidatosSearchInput) this.candidatosSearchInput.value = '';
    document.querySelectorAll(".btn-cand-filter").forEach(b => {
      b.classList.toggle('active', b.dataset.filter === 'todos');
    });

    if (this.candidatosModalTitle) {
      this.candidatosModalTitle.textContent = `Postulantes: ${item.titulo}`;
    }
    if (this.candidatosModalCompany) {
      this.candidatosModalCompany.textContent = `${item.empresa || 'UNI'} • Modalidad ${item.modalidad} • ${item.duracion}`;
    }
    if (this.candidatosPasantiaStatusBadge) {
      const isFin = item.estado === 'Finalizado';
      this.candidatosPasantiaStatusBadge.textContent = isFin ? 'Historial (Finalizada)' : 'Convocatoria Activa';
      this.candidatosPasantiaStatusBadge.className = 'badge-status-pasantia ' + (isFin ? 'status-historial' : 'status-activa');
    }

    this.renderCandidatosTable();
    this.modalCandidatos?.classList.add("is-visible");
  }

  closeCandidatosModal() {
    this.modalCandidatos?.classList.remove("is-visible");
    this.activeCandPasantia = null;
  }

  renderCandidatosTable() {
    if (!this.activeCandPasantia) return;
    const pId = this.activeCandPasantia.id;

    // Todas las solicitudes para esta pasantía
    const allForPasantia = this.solicitudes.filter(s => s.pasantiaId === pId);

    // Actualizar estadísticas de la barra superior
    const total = allForPasantia.length;
    const pendientes = allForPasantia.filter(s => s.estado === 'pendiente').length;
    const aceptados = allForPasantia.filter(s => s.estado === 'aceptado').length;
    const rechazados = allForPasantia.filter(s => s.estado === 'rechazado').length;

    if (this.statCountTotal) this.statCountTotal.textContent = total;
    if (this.statCountPendientes) this.statCountPendientes.textContent = pendientes;
    if (this.statCountAceptados) this.statCountAceptados.textContent = aceptados;
    if (this.statCountRechazados) this.statCountRechazados.textContent = rechazados;

    // Filtrar por estado y buscador
    let filtered = allForPasantia.filter(s => {
      if (this.candFilterState !== 'todos' && s.estado !== this.candFilterState) {
        return false;
      }
      if (this.candSearchQuery) {
        const q = this.candSearchQuery;
        const matches = s.nombre.toLowerCase().includes(q) ||
                        s.email.toLowerCase().includes(q) ||
                        (s.carrera && s.carrera.toLowerCase().includes(q));
        if (!matches) return false;
      }
      return true;
    });

    if (this.candidatosFooterInfo) {
      this.candidatosFooterInfo.textContent = `Mostrando ${filtered.length} de ${total} postulante${total === 1 ? '' : 's'}`;
    }

    if (filtered.length === 0) {
      if (this.candidatosTableTbody) this.candidatosTableTbody.innerHTML = '';
      if (this.candidatosEmptyState) this.candidatosEmptyState.style.display = 'flex';
      this.initLucideIcons();
      return;
    }

    if (this.candidatosEmptyState) this.candidatosEmptyState.style.display = 'none';

    if (this.candidatosTableTbody) {
      this.candidatosTableTbody.innerHTML = filtered.map((s, index) => {
        const fechaFormat = this.formatFecha(s.fechaSolicitud);
        const estadoBadge = s.estado === 'aceptado'
          ? `<span class="badge-cand-estado cand-aceptado"><i data-lucide="check-circle-2"></i> Aceptado</span>`
          : s.estado === 'rechazado'
          ? `<span class="badge-cand-estado cand-rechazado"><i data-lucide="x-circle"></i> Rechazado</span>`
          : `<span class="badge-cand-estado cand-pendiente"><i data-lucide="clock"></i> Pendiente</span>`;

        // Botón o enlace de descarga de CV
        const cvBtn = s.cvFileData
          ? `<a href="${s.cvFileData}" download="${s.cvFileName || 'CV_Postulante'}" class="btn-descargar-cv" title="Descargar archivo">
               <i data-lucide="paperclip"></i>
               <span>${s.cvFileName || 'Ver CV'}</span>
               <span class="cv-table-size">(${s.cvFileSize || 'Descargar'})</span>
             </a>`
          : `<span class="btn-descargar-cv is-placeholder" title="Documento registrado: ${s.cvFileName}">
               <i data-lucide="file-text"></i>
               <span>${s.cvFileName || 'CV.pdf'}</span>
             </span>`;

        return `
          <tr data-sol-id="${s.id}">
            <td class="td-index">${index + 1}</td>
            <td class="td-postulante">
              <div class="cand-cell-user">
                <div class="cand-avatar">${s.nombre.charAt(0)}</div>
                <div class="cand-user-meta">
                  <span class="cand-name">${s.nombre}</span>
                  <span class="cand-carrera">${s.carrera || 'Estudiante UNI'}</span>
                </div>
              </div>
            </td>
            <td class="td-contacto">
              <span class="cand-email">${s.email}</span>
              <span class="cand-tel">${s.telefono || 'Sin teléfono'}</span>
            </td>
            <td class="td-fecha">${fechaFormat}</td>
            <td class="td-cv">${cvBtn}</td>
            <td class="td-estado">${estadoBadge}</td>
            <td class="td-acciones">
              <div class="cand-actions-btn-group">
                <button type="button" class="btn-cand-action btn-cand-accept ${s.estado === 'aceptado' ? 'is-selected' : ''}" 
                        onclick="window.pasantiasApp.aceptarCandidato('${s.id}')" title="Aceptar postulante">
                  <i data-lucide="check"></i>
                </button>
                <button type="button" class="btn-cand-action btn-cand-reject ${s.estado === 'rechazado' ? 'is-selected' : ''}" 
                        onclick="window.pasantiasApp.rechazarCandidato('${s.id}')" title="Rechazar postulante">
                  <i data-lucide="x"></i>
                </button>
              </div>
            </td>
          </tr>
        `;
      }).join('');
    }

    this.initLucideIcons();
  }

  aceptarCandidato(solId) {
    const solicitud = this.solicitudes.find(s => s.id === solId);
    if (!solicitud) return;

    solicitud.estado = "aceptado";
    this.saveSolicitudes();

    // Notificación para el estudiante
    this.addNotificacion(
      "candidato_aceptado",
      "¡Felicidades! Fuiste Aceptado",
      `Tu postulación para la "${solicitud.pasantiaTitulo}" ha sido ACEPTADA por el departamento evaluador.`,
      solicitud.pasantiaId
    );

    this.renderCandidatosTable();
    this.renderGrid();
    this.showToast(`Candidato "${solicitud.nombre}" ACEPTADO correctamente. Se notificó al estudiante.`, "success");
  }

  rechazarCandidato(solId) {
    const solicitud = this.solicitudes.find(s => s.id === solId);
    if (!solicitud) return;

    solicitud.estado = "rechazado";
    this.saveSolicitudes();

    // Notificación para el estudiante
    this.addNotificacion(
      "candidato_rechazado",
      "Actualización de Postulación",
      `Tu solicitud para "${solicitud.pasantiaTitulo}" ha sido finalizada con estatus no seleccionada.`,
      solicitud.pasantiaId
    );

    this.renderCandidatosTable();
    this.renderGrid();
    this.showToast(`Candidato "${solicitud.nombre}" marcado como rechazado.`, "info");
  }

  // --------------------------------------------------------------------------
  // EXPORTACIÓN A CSV CON BOM UTF-8 (COMPATIBLE CON EXCEL)
  // --------------------------------------------------------------------------
  exportarCandidatosCSV() {
    if (!this.activeCandPasantia) return;
    const pId = this.activeCandPasantia.id;
    const candidatos = this.solicitudes.filter(s => s.pasantiaId === pId);

    if (candidatos.length === 0) {
      this.showToast("No hay candidatos registrados en esta pasantía para exportar.", "info");
      return;
    }

    // Cabecera CSV
    const headers = [
      "#",
      "ID Solicitud",
      "Pasantía",
      "Nombre Completo",
      "Correo Electrónico",
      "Teléfono",
      "Carrera / Año",
      "Nombre Archivo CV",
      "Fecha de Solicitud",
      "Estado Postulación",
      "Mensaje de Presentación"
    ];

    // Helper para escapar comillas dobles en campos CSV
    const escapeCSV = (val) => {
      if (val === null || val === undefined) return '""';
      const str = String(val).replace(/"/g, '""');
      return `"${str}"`;
    };

    const rows = candidatos.map((c, idx) => [
      escapeCSV(idx + 1),
      escapeCSV(c.id),
      escapeCSV(c.pasantiaTitulo),
      escapeCSV(c.nombre),
      escapeCSV(c.email),
      escapeCSV(c.telefono || 'N/A'),
      escapeCSV(c.carrera || 'N/A'),
      escapeCSV(c.cvFileName || 'N/A'),
      escapeCSV(c.fechaSolicitud),
      escapeCSV(c.estado.toUpperCase()),
      escapeCSV(c.mensaje || '')
    ]);

    // Unir todo con salto de línea estándar
    const csvContent = [
      headers.map(escapeCSV).join(";"),
      ...rows.map(r => r.join(";"))
    ].join("\r\n");

    // Agregar UTF-8 BOM (\uFEFF) para que Excel abra acentos, tildes y caracteres especiales con total nitidez
    const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const safeTitle = this.activeCandPasantia.titulo
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '_')
      .replace(/_+/g, '_');
    const fechaDescarga = new Date().toISOString().slice(0, 10);
    const fileName = `candidatos_${safeTitle}_${fechaDescarga}.csv`;

    const downloadLink = document.createElement("a");
    downloadLink.href = url;
    downloadLink.setAttribute("download", fileName);
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
    URL.revokeObjectURL(url);

    this.showToast(`¡Lista de postulantes (${candidatos.length}) exportada exitosamente a ${fileName}!`, "success");
  }

  formatFecha(isoStr) {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('es-NI', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch (_) {
      return isoStr;
    }
  }

  // --------------------------------------------------------------------------
  // SISTEMA DE NOTIFICACIONES
  // --------------------------------------------------------------------------
  addNotificacion(tipo, titulo, mensaje, pasantiaId = null) {
    const nuevaNotif = {
      id: "notif-" + Date.now() + "-" + Math.floor(Math.random() * 1000),
      tipo,
      titulo,
      mensaje,
      pasantiaId,
      fecha: new Date().toISOString(),
      leida: false
    };

    this.notificaciones.unshift(nuevaNotif);
    this.saveNotificaciones();
    this.renderNotificaciones();
    this.updateNotifBadge();
  }

  renderNotificaciones() {
    if (!this.drawerNotifsList) return;

    if (this.notificaciones.length === 0) {
      this.drawerNotifsList.innerHTML = `
        <div class="empty-notifs-box">
          <i data-lucide="bell-off"></i>
          <p>No tienes notificaciones pendientes</p>
        </div>
      `;
      this.initLucideIcons();
      return;
    }

    this.drawerNotifsList.innerHTML = this.notificaciones.map(n => {
      const iconName = n.tipo === 'candidato_aceptado' ? 'check-circle'
                     : n.tipo === 'candidato_rechazado' ? 'alert-triangle'
                     : n.tipo === 'pasantia_finalizada' || n.tipo === 'favorito_finalizado' ? 'clock'
                     : 'bell';

      const accentColor = n.tipo === 'candidato_aceptado' ? '#00C853'
                        : n.tipo === 'candidato_rechazado' ? '#EF4444'
                        : '#3B82F6';

      return `
        <div class="notification-card-item" data-notif-id="${n.id}">
          <div class="notif-avatar-col">
            <div class="notif-avatar-circle" style="border-color: ${accentColor}; color: ${accentColor};">
              <i data-lucide="${iconName}"></i>
            </div>
          </div>
          <div class="notif-body-col">
            <h5 class="notif-title">${n.titulo}</h5>
            <p class="notif-text">${n.mensaje}</p>
            <div class="notif-buttons-row">
              <span class="notif-time-badge">${this.formatFecha(n.fecha)}</span>
              ${n.pasantiaId ? `
                <button type="button" class="btn-notif-vermas" onclick="window.pasantiasApp.openPasantiaFromNotif(${n.pasantiaId})">
                  Ver pasantía
                </button>
              ` : ''}
            </div>
          </div>
          <button type="button" class="btn-notif-dismiss" onclick="window.pasantiasApp.dismissNotificacion('${n.id}')" title="Descartar notificación">
            <i data-lucide="x"></i>
          </button>
        </div>
      `;
    }).join("");

    this.initLucideIcons();
  }

  openPasantiaFromNotif(pasantiaId) {
    this.closeDrawer();
    const card = document.getElementById(`pasantia-card-${pasantiaId}`);
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      card.classList.add('pasantia-card-highlight');
      setTimeout(() => card.classList.remove('pasantia-card-highlight'), 2500);
    } else {
      this.showToast("La pasantía referida se encuentra archivada o no está disponible.", "info");
    }
  }

  dismissNotificacion(notifId) {
    this.notificaciones = this.notificaciones.filter(n => n.id !== notifId);
    this.saveNotificaciones();
    this.renderNotificaciones();
    this.updateNotifBadge();
  }

  clearAllNotificaciones() {
    this.notificaciones = [];
    this.saveNotificaciones();
    this.renderNotificaciones();
    this.updateNotifBadge();
    this.showToast("Notificaciones limpiadas", "info");
  }

  updateNotifBadge() {
    const unread = this.notificaciones.filter(n => !n.leida).length;
    if (this.notifBadgeCount) {
      this.notifBadgeCount.textContent = unread;
      this.notifBadgeCount.style.display = unread > 0 ? 'flex' : 'none';
    }
  }

  // --------------------------------------------------------------------------
  // MODAL CREAR PASANTÍA (ADMIN)
  // --------------------------------------------------------------------------
  openModal() {
    this.modalOverlay?.classList.add("is-visible");
  }

  closeModal() {
    this.modalOverlay?.classList.remove("is-visible");
    this.formAgregarPasantia?.reset();
  }

  handleCreatePasantia(e) {
    e.preventDefault();
    const titulo = document.getElementById("modal-pasantia-titulo")?.value.trim() || "Nueva Pasantía";
    const tipo = document.getElementById("modal-pasantia-tipo")?.value || "Académica";
    const modalidad = document.getElementById("modal-pasantia-modalidad")?.value || "Presencial";
    const duracion = document.getElementById("modal-pasantia-horas")?.value.trim() || "160H";
    const experiencia = document.getElementById("modal-pasantia-experiencia")?.value || "Sin experiencia";
    const sector = document.getElementById("modal-pasantia-sector")?.value || "Tecnología";
    const ciudad = document.getElementById("modal-pasantia-ciudad")?.value || "Managua";
    const descripcion = document.getElementById("modal-pasantia-desc")?.value.trim() || "Descripción institucional.";

    const nuevaPasantia = {
      id: Date.now(),
      titulo,
      tipo,
      modalidad,
      duracion,
      experiencia,
      sector,
      ciudad,
      descripcion,
      empresa: "Universidad Nacional de Ingeniería",
      requisitos: "Estudiantes activos con carné vigente.",
      beneficios: "Certificado oficial de prácticas y carta de recomendación.",
      estado: "Activo"
    };

    this.pasantias.unshift(nuevaPasantia);
    this.savePasantias();
    this.closeModal();
    this.updateTabCounts();
    this.renderGrid();
    this.showToast(`Pasantía "${titulo}" publicada con éxito.`, "success");
  }

  // --------------------------------------------------------------------------
  // DROPDOWNS & DRAWER
  // --------------------------------------------------------------------------
  initFilterDropdowns() {
    const filterContainers = document.querySelectorAll(".filter-dropdown-container");
    filterContainers.forEach(container => {
      const button = container.querySelector(".filter-pill-button");
      const menu = container.querySelector(".filter-dropdown-menu");
      const filterKey = container.dataset.filterKey;

      if (!button || !menu) return;

      button.addEventListener("click", (e) => {
        e.stopPropagation();
        document.querySelectorAll(".filter-dropdown-menu.show").forEach(m => {
          if (m !== menu) m.classList.remove("show");
        });
        menu.classList.toggle("show");
      });

      menu.querySelectorAll(".filter-dropdown-item").forEach(item => {
        item.addEventListener("click", () => {
          const val = item.dataset.value;
          const label = item.dataset.label || item.textContent.trim();
          this.filters[filterKey] = val;

          const textSpan = button.querySelector(".pill-text");
          if (textSpan) {
            textSpan.textContent = val ? label.toUpperCase() : filterKey.toUpperCase();
          }

          if (val) {
            button.classList.add("is-active");
          } else {
            button.classList.remove("is-active");
          }

          menu.classList.remove("show");
          this.renderGrid();
        });
      });
    });

    document.addEventListener("click", () => {
      document.querySelectorAll(".filter-dropdown-menu.show").forEach(m => m.classList.remove("show"));
    });
  }

  openDrawer() {
    document.body.classList.add("drawer-opened");
    this.drawerBackdrop?.classList.add("is-active");
    this.drawerPanel?.classList.add("is-open");
  }

  closeDrawer() {
    document.body.classList.remove("drawer-opened");
    this.drawerBackdrop?.classList.remove("is-active");
    this.drawerPanel?.classList.remove("is-open");
  }

  showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      container.className = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `custom-floating-toast toast-${type}`;
    toast.style.cssText = `
      background: ${type === 'success' ? '#00C853' : type === 'error' ? '#EF4444' : '#0B1B48'};
      color: #FFFFFF;
      padding: 12px 18px;
      border-radius: 10px;
      font-size: 13.5px;
      font-weight: 600;
      box-shadow: 0 10px 25px rgba(0,0,0,0.25);
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 10px;
      animation: fadeInToast 0.25s ease-out;
      z-index: 10000;
    `;
    toast.textContent = message;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-10px)";
      toast.style.transition = "all 0.25s ease";
      setTimeout(() => toast.remove(), 250);
    }, 3500);
  }

  initLucideIcons() {
    if (typeof lucide !== "undefined" && lucide.createIcons) {
      lucide.createIcons();
    }
  }
}

// Inicializar y exponer en window
window.pasantiasApp = new PasantiasApp();
