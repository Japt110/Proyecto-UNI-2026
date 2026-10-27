/**
 * ==============================================================================
 * PASANTÍAS UNI - CONTROLADOR DE INTERFAZ FIEL AL PDF
 * Gestiona: Vista Admin, Vista Usuario, Detalle Interactivo, Drawer Lateral,
 * Filtros en tiempo real, Notificaciones y Creación de Pasantías.
 * ==============================================================================
 */

// Datos semilla de pasantías fieles al diseño del PDF
const DEFAULT_PASANTIAS = [
  {
    id: 1,
    titulo: "Pasantia #1",
    tipo: "Académica",
    modalidad: "Presencial",
    duracion: "160H",
    experiencia: "Sin experiencia",
    sector: "Tecnología",
    ciudad: "Managua",
    descripcion: "Detalles de la de la pasantia. Prácticas profesionales en desarrollo de software, análisis de sistemas institucionales y administración de bases de datos.",
    estado: "Activo"
  },
  {
    id: 2,
    titulo: "Pasantia",
    tipo: "Académica",
    modalidad: "Presencial",
    duracion: "160H",
    experiencia: "Prácticas",
    sector: "Química",
    ciudad: "Chinandega",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  },
  {
    id: 3,
    titulo: "Pasantia",
    tipo: "Profesional",
    modalidad: "Virtual",
    duracion: "240H",
    experiencia: "Junior",
    sector: "Industrial",
    ciudad: "León",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  },
  {
    id: 4,
    titulo: "Pasantia",
    tipo: "Académica",
    modalidad: "Presencial",
    duracion: "160H",
    experiencia: "Sin experiencia",
    sector: "Civil",
    ciudad: "Estelí",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  },
  {
    id: 5,
    titulo: "Pasantia",
    tipo: "Profesional",
    modalidad: "Híbrida",
    duracion: "320H",
    experiencia: "Prácticas",
    sector: "Eléctrica",
    ciudad: "Managua",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  },
  {
    id: 6,
    titulo: "Pasantia",
    tipo: "Académica",
    modalidad: "Presencial",
    duracion: "160H",
    experiencia: "Sin experiencia",
    sector: "Tecnología",
    ciudad: "Managua",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  },
  {
    id: 7,
    titulo: "Pasantia",
    tipo: "Académica",
    modalidad: "Presencial",
    duracion: "160H",
    experiencia: "Prácticas",
    sector: "Industrial",
    ciudad: "Matagalpa",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  },
  {
    id: 8,
    titulo: "Pasantia",
    tipo: "Profesional",
    modalidad: "Virtual",
    duracion: "200H",
    experiencia: "Junior",
    sector: "Química",
    ciudad: "Chinandega",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  },
  {
    id: 9,
    titulo: "Pasantia",
    tipo: "Académica",
    modalidad: "Presencial",
    duracion: "160H",
    experiencia: "Sin experiencia",
    sector: "Sistemas",
    ciudad: "Managua",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  },
  {
    id: 10,
    titulo: "Pasantia",
    tipo: "Académica",
    modalidad: "Presencial",
    duracion: "160H",
    experiencia: "Prácticas",
    sector: "Civil",
    ciudad: "Juigalpa",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  },
  {
    id: 11,
    titulo: "Pasantia",
    tipo: "Profesional",
    modalidad: "Híbrida",
    duracion: "240H",
    experiencia: "Junior",
    sector: "Industrial",
    ciudad: "Managua",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  },
  {
    id: 12,
    titulo: "Pasantia",
    tipo: "Académica",
    modalidad: "Presencial",
    duracion: "160H",
    experiencia: "Sin experiencia",
    sector: "Tecnología",
    ciudad: "León",
    descripcion: "lorem ipsum lorem lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
    estado: "Activo"
  }
];

class PasantiasApp {
  constructor() {
    this.pasantias = this.loadPasantias();
    this.currentRole = this.getInitialRole(); // 'admin' | 'usuario'
    this.expandedCardId = null;
    this.filters = {
      search: "",
      experiencia: "",
      modalidad: "",
      sector: "",
      ciudad: ""
    };

    this.init();
  }

  loadPasantias() {
    try {
      const stored = localStorage.getItem("uni_pasantias_data");
      if (stored) return JSON.parse(stored);
    } catch (_) {}
    return [...DEFAULT_PASANTIAS];
  }

  savePasantias() {
    try {
      localStorage.setItem("uni_pasantias_data", JSON.stringify(this.pasantias));
    } catch (_) {}
  }

  getInitialRole() {
    // 1. Revisar parámetro de URL (?role=admin o ?role=usuario)
    const urlParams = new URLSearchParams(window.location.search);
    const roleParam = urlParams.get("role");
    if (roleParam === "admin" || roleParam === "usuario") {
      localStorage.setItem("uni_current_view_role", roleParam);
      return roleParam;
    }
    // 2. Revisar almacenamiento local
    const savedRole = localStorage.getItem("uni_current_view_role");
    return savedRole === "usuario" ? "usuario" : "admin";
  }

  init() {
    document.addEventListener("DOMContentLoaded", () => {
      this.bindElements();
      this.bindEvents();
      this.applyRole(this.currentRole);
      this.renderGrid();
      this.initLucideIcons();
    });
  }

  bindElements() {
    this.pageWrapper = document.getElementById("pasantias-wrapper");
    this.gridContainer = document.getElementById("pasantias-grid");
    this.searchInput = document.getElementById("pasantias-search-input");
    this.roleToggleAdmin = document.getElementById("role-toggle-admin");
    this.roleToggleUsuario = document.getElementById("role-toggle-usuario");
    this.btnAgregarPasantia = document.getElementById("btn-agregar-pasantia");
    
    // Drawer elements
    this.btnProfileTrigger = document.getElementById("btn-profile-trigger");
    this.drawerPanel = document.getElementById("uni-drawer-panel");
    this.drawerBackdrop = document.getElementById("uni-drawer-backdrop");
    this.btnDrawerCollapse = document.getElementById("btn-drawer-collapse");
    this.btnDrawerLogout = document.getElementById("btn-drawer-logout");

    // Modal elements
    this.modalOverlay = document.getElementById("modal-agregar-pasantia");
    this.btnCloseModal = document.getElementById("btn-close-modal");
    this.btnCancelModal = document.getElementById("btn-cancel-modal");
    this.formAgregarPasantia = document.getElementById("form-agregar-pasantia");
  }

  bindEvents() {
    // 1. Conmutador de Roles
    if (this.roleToggleAdmin) {
      this.roleToggleAdmin.addEventListener("click", () => this.setRole("admin"));
    }
    if (this.roleToggleUsuario) {
      this.roleToggleUsuario.addEventListener("click", () => this.setRole("usuario"));
    }

    // 2. Drawer de Perfil & Ajustes (Página 7)
    if (this.btnProfileTrigger) {
      this.btnProfileTrigger.addEventListener("click", (e) => {
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
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.closeDrawer();
        this.closeModal();
      }
    });

    // 3. Búsqueda en tiempo real
    if (this.searchInput) {
      this.searchInput.addEventListener("input", (e) => {
        this.filters.search = e.target.value.toLowerCase().trim();
        this.renderGrid();
      });
    }

    // 4. Dropdowns de Filtros (EXPERIENCIA, MODALIDAD, SECTOR, CIUDAD)
    this.initFilterDropdowns();

    // 5. Modal Agregar Pasantía (Vista Admin)
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

    // 6. Cerrar Sesión
    if (this.btnDrawerLogout) {
      this.btnDrawerLogout.addEventListener("click", (e) => {
        e.preventDefault();
        window.location.href = "/login";
      });
    }

    // 7. Notificaciones en el Drawer
    this.initNotificationActions();
  }

  setRole(role) {
    this.currentRole = role;
    localStorage.setItem("uni_current_view_role", role);
    this.applyRole(role);
    this.renderGrid();
    this.showToast(`Modo cambiado a: Vista ${role === 'admin' ? 'Administrador' : 'Usuario'}`, "info");
  }

  applyRole(role) {
    if (role === "admin") {
      this.pageWrapper?.classList.remove("view-usuario-mode");
      this.pageWrapper?.classList.add("view-admin-mode");
      this.roleToggleAdmin?.classList.add("active");
      this.roleToggleUsuario?.classList.remove("active");
    } else {
      this.pageWrapper?.classList.remove("view-admin-mode");
      this.pageWrapper?.classList.add("view-usuario-mode");
      this.roleToggleAdmin?.classList.remove("active");
      this.roleToggleUsuario?.classList.add("active");
    }
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

  openModal() {
    this.modalOverlay?.classList.add("is-visible");
  }

  closeModal() {
    this.modalOverlay?.classList.remove("is-visible");
    this.formAgregarPasantia?.reset();
  }

  initFilterDropdowns() {
    const filterContainers = document.querySelectorAll(".filter-dropdown-container");
    filterContainers.forEach(container => {
      const button = container.querySelector(".filter-pill-button");
      const menu = container.querySelector(".filter-dropdown-menu");
      const filterKey = container.dataset.filterKey;

      if (!button || !menu) return;

      button.addEventListener("click", (e) => {
        e.stopPropagation();
        // Cerrar otros dropdowns abiertos
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

          // Actualizar texto del botón
          const textSpan = button.querySelector(".pill-text");
          if (textSpan) {
            textSpan.textContent = val ? label.toUpperCase() : filterKey.toUpperCase();
          }

          // Si tiene valor seleccionado, aplicar clase highlight-blue como en el PDF
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

    // Cerrar al hacer clic fuera
    document.addEventListener("click", () => {
      document.querySelectorAll(".filter-dropdown-menu.show").forEach(m => m.classList.remove("show"));
    });
  }

  renderGrid() {
    if (!this.gridContainer) return;

    // Filtrar pasantías
    const filtered = this.pasantias.filter(p => {
      // Búsqueda libre
      if (this.filters.search) {
        const query = this.filters.search;
        const matchesText = p.titulo.toLowerCase().includes(query) ||
                            p.descripcion.toLowerCase().includes(query) ||
                            p.sector.toLowerCase().includes(query) ||
                            p.ciudad.toLowerCase().includes(query);
        if (!matchesText) return false;
      }
      // Filtros específicos
      if (this.filters.experiencia && p.experiencia.toLowerCase() !== this.filters.experiencia.toLowerCase()) return false;
      if (this.filters.modalidad && p.modalidad.toLowerCase() !== this.filters.modalidad.toLowerCase()) return false;
      if (this.filters.sector && p.sector.toLowerCase() !== this.filters.sector.toLowerCase()) return false;
      if (this.filters.ciudad && p.ciudad.toLowerCase() !== this.filters.ciudad.toLowerCase()) return false;

      return true;
    });

    if (filtered.length === 0) {
      this.gridContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: #64748B;">
          <i data-lucide="inbox" style="width: 48px; height: 48px; margin: 0 auto 12px; display: block; opacity: 0.5;"></i>
          <h4 style="font-size: 16px; font-weight: 600; color: #334155;">No se encontraron pasantías</h4>
          <p style="font-size: 13px;">Prueba ajustando los filtros de búsqueda seleccionados.</p>
        </div>
      `;
      this.initLucideIcons();
      return;
    }

    this.gridContainer.innerHTML = filtered.map(p => {
      const isExpanded = this.expandedCardId === p.id;
      return `
        <div class="pasantia-card ${isExpanded ? 'is-expanded' : ''}" data-id="${p.id}" id="pasantia-card-${p.id}">
          <img src="/static/img/pasantia_banner.jpg" alt="Pasantía UNI" class="pasantia-card-banner" />
          <div class="pasantia-card-body">
            <h3 class="pasantia-card-title">${p.titulo}</h3>
            
            ${isExpanded ? `
              <div class="pasantia-badges-row">
                <span class="pasantia-badge">${p.tipo}</span>
                <span class="pasantia-badge badge-presencial">${p.modalidad}</span>
                <span class="pasantia-badge">${p.duracion}</span>
              </div>
            ` : ''}

            <span class="pasantia-card-desc-label">Descripcion:</span>
            <p class="pasantia-card-desc-text">${p.descripcion}</p>

            ${isExpanded ? `
              <div class="pasantia-actions-row">
                <button type="button" class="btn-pasantia-guardar" onclick="event.stopPropagation(); window.pasantiasApp.guardarPasantia(${p.id})">
                  GUARDAR
                </button>
                <button type="button" class="btn-pasantia-solicitar" onclick="event.stopPropagation(); window.pasantiasApp.solicitarPasantia(${p.id})">
                  SOLICITAR
                </button>
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }).join("");

    // Agregar listeners a las tarjetas para expandir/contraer
    this.gridContainer.querySelectorAll(".pasantia-card").forEach(card => {
      card.addEventListener("click", () => {
        const id = parseInt(card.dataset.id, 10);
        this.toggleCardExpand(id);
      });
    });

    this.initLucideIcons();
  }

  toggleCardExpand(id) {
    if (this.expandedCardId === id) {
      this.expandedCardId = null;
      // Restaurar estado visual del filtro si se deselecciona
      this.resetModalidadFilterHighlight();
    } else {
      this.expandedCardId = id;
      // Al expandir la primera tarjeta (Pág 6 del PDF), resaltar el filtro MODALIDAD -> PRESENCIAL
      const pasantia = this.pasantias.find(p => p.id === id);
      if (pasantia && pasantia.modalidad === "Presencial") {
        this.highlightModalidadPresencial();
      }
    }
    this.renderGrid();
  }

  highlightModalidadPresencial() {
    const modBtn = document.getElementById("btn-filter-modalidad");
    if (modBtn) {
      modBtn.classList.add("highlight-blue");
      const textSpan = modBtn.querySelector(".pill-text");
      if (textSpan) textSpan.textContent = "PRESENCIAL";
    }
  }

  resetModalidadFilterHighlight() {
    if (!this.filters.modalidad) {
      const modBtn = document.getElementById("btn-filter-modalidad");
      if (modBtn) {
        modBtn.classList.remove("highlight-blue");
        const textSpan = modBtn.querySelector(".pill-text");
        if (textSpan) textSpan.textContent = "MODALIDAD";
      }
    }
  }

  guardarPasantia(id) {
    const item = this.pasantias.find(p => p.id === id);
    if (!item) return;
    this.showToast(`Pasantía "${item.titulo}" guardada en tus favoritos`, "success");
  }

  solicitarPasantia(id) {
    const item = this.pasantias.find(p => p.id === id);
    if (!item) return;

    this.showToast(`¡Solicitud enviada con éxito para ${item.titulo}!`, "success");

    // Agregar notificación dinámica al Drawer
    const notifContainer = document.getElementById("drawer-notifications-list");
    if (notifContainer) {
      const newNotif = document.createElement("div");
      newNotif.className = "notification-card-item";
      newNotif.innerHTML = `
        <div class="notif-avatar-col">
          <div class="notif-avatar-circle"><i data-lucide="user"></i></div>
        </div>
        <div class="notif-body-col">
          <h5 class="notif-title">${item.titulo}</h5>
          <p class="notif-text">Solicitud de pasantía registrada correctamente en estado Pendiente.</p>
          <div class="notif-buttons-row">
            <button class="btn-notif-aceptar" onclick="window.pasantiasApp.showToast('Solicitud aceptada', 'success')">Aceptar</button>
            <button class="btn-notif-vermas" onclick="window.pasantiasApp.showToast('Detalles de pasantía consultados', 'info')">Ver mas</button>
          </div>
        </div>
        <button class="btn-notif-dismiss" onclick="this.closest('.notification-card-item').remove()" title="Descartar">
          <i data-lucide="x"></i>
        </button>
      `;
      notifContainer.prepend(newNotif);
      this.initLucideIcons();
    }
  }

  handleCreatePasantia(e) {
    e.preventDefault();
    const titulo = document.getElementById("modal-pasantia-titulo")?.value.trim() || "Pasantia";
    const tipo = document.getElementById("modal-pasantia-tipo")?.value || "Académica";
    const modalidad = document.getElementById("modal-pasantia-modalidad")?.value || "Presencial";
    const duracion = document.getElementById("modal-pasantia-horas")?.value.trim() || "160H";
    const experiencia = document.getElementById("modal-pasantia-experiencia")?.value || "Sin experiencia";
    const sector = document.getElementById("modal-pasantia-sector")?.value || "Tecnología";
    const ciudad = document.getElementById("modal-pasantia-ciudad")?.value || "Managua";
    const descripcion = document.getElementById("modal-pasantia-desc")?.value.trim() || "lorem ipsum lorem lorem ipsum lorem";

    const newId = Date.now();
    const nuevaPasantia = {
      id: newId,
      titulo,
      tipo,
      modalidad,
      duracion,
      experiencia,
      sector,
      ciudad,
      descripcion,
      estado: "Activo"
    };

    this.pasantias.unshift(nuevaPasantia);
    this.savePasantias();
    this.closeModal();
    this.renderGrid();
    this.showToast("Nueva pasantía agregada correctamente al catálogo", "success");
  }

  initNotificationActions() {
    document.querySelectorAll(".btn-notif-dismiss").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const item = e.target.closest(".notification-card-item");
        if (item) {
          item.remove();
          this.showToast("Notificación descartada", "info");
        }
      });
    });
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
    }, 3200);
  }

  initLucideIcons() {
    if (typeof lucide !== "undefined" && lucide.createIcons) {
      lucide.createIcons();
    }
  }
}

// Inicializar y exponer en window
window.pasantiasApp = new PasantiasApp();
