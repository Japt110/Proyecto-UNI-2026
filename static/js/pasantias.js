/**
 * ==============================================================================
 * SISTEMA WEB DE CONTROL DE PASANTÍAS - CONTROLADOR CRUD REAL CON SQLALCHEMY
 * Conecta directamente con las APIs RESTful del backend:
 * - GET  /api/auth/me                      : Identidad y rol en sesión activa
 * - POST /api/auth/logout                  : Cierre formal de sesión
 * - GET  /api/pasantias                    : Catálogo y filtrado de ofertas
 * - POST /api/pasantias                    : Creación de nueva oferta (Admin/Empresa)
 * - GET  /api/pasantias/<id>               : Consulta de detalle de oferta
 * - PUT  /api/pasantias/<id>               : Actualización de oferta
 * - DELETE /api/pasantias/<id>             : Eliminación de oferta
 * - POST /api/pasantias/<id>/aplicar       : Postulación de estudiante (CU-03)
 * - GET  /api/pasantias/mis-aplicaciones   : Historial de postulaciones (CU-04)
 * - GET  /api/pasantias/<id>/aplicaciones  : Evaluación de candidatos (CU-07)
 * - PUT  /api/pasantias/aplicaciones/<id>/estado : Transición y aprobación (CU-07)
 * - PUT  /api/empresas/<id>/aprobar        : Aprobación institucional (CU-08)
 * ==============================================================================
 */

class PasantiasApp {
  constructor() {
    this.currentUser = null;
    this.pasantias = [];
    this.misAplicaciones = new Map(); // id_oferta -> aplicacion
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

  async init() {
    document.addEventListener("DOMContentLoaded", async () => {
      this.bindElements();
      this.bindEvents();
      this.initFilterDropdowns();
      await this.fetchCurrentUser();
      await this.loadPasantias();
      this.initLucideIcons();
    });
  }

  bindElements() {
    this.pageWrapper = document.getElementById("pasantias-wrapper");
    this.gridContainer = document.getElementById("pasantias-grid");
    this.searchInput = document.getElementById("pasantias-search-input");
    this.btnAgregarPasantia = document.getElementById("btn-agregar-pasantia");
    this.adminActionContainer = document.getElementById("admin-action-container");
    this.statusTextCount = document.getElementById("status-text-count");
    this.topbarUserBadge = document.getElementById("topbar-user-badge");

    // Drawer elements
    this.btnProfileTrigger = document.getElementById("btn-profile-trigger");
    this.drawerPanel = document.getElementById("uni-drawer-panel");
    this.drawerBackdrop = document.getElementById("uni-drawer-backdrop");
    this.btnDrawerCollapse = document.getElementById("btn-drawer-collapse");
    this.btnDrawerLogout = document.getElementById("btn-drawer-logout");
    this.drawerUserName = document.getElementById("drawer-user-name");
    this.drawerUserCup = document.getElementById("drawer-user-cup");
    this.drawerUserEmail = document.getElementById("drawer-user-email");
    this.drawerNotificationsList = document.getElementById("drawer-notifications-list");
    this.drawerNotifHeading = document.getElementById("drawer-notif-heading");

    // Modal Pasantía elements
    this.modalPasantia = document.getElementById("modal-agregar-pasantia");
    this.modalPasantiaTitle = document.getElementById("modal-pasantia-form-title");
    this.modalPasantiaId = document.getElementById("modal-pasantia-id");
    this.btnCloseModal = document.getElementById("btn-close-modal");
    this.btnCancelModal = document.getElementById("btn-cancel-modal");
    this.formAgregarPasantia = document.getElementById("form-agregar-pasantia");

    // Modal Postulantes elements
    this.modalPostulantes = document.getElementById("modal-postulantes");
    this.modalPostulantesTitle = document.getElementById("modal-postulantes-titulo");
    this.modalPostulantesBody = document.getElementById("modal-postulantes-body");
    this.btnCloseModalPostulantes = document.getElementById("btn-close-modal-postulantes");

    // Modal Aplicar Pasantía elements (CU-03)
    this.modalAplicar = document.getElementById("modal-aplicar-pasantia");
    this.modalAplicarOfertaId = document.getElementById("modal-aplicar-oferta-id");
    this.modalAplicarOfertaTitulo = document.getElementById("modal-aplicar-oferta-titulo");
    this.modalAplicarOfertaEmpresa = document.getElementById("modal-aplicar-oferta-empresa");
    this.modalAplicarDocsContainer = document.getElementById("modal-aplicar-docs-container");
    this.modalAplicarMotivo = document.getElementById("modal-aplicar-motivo");
    this.btnCloseModalAplicar = document.getElementById("btn-close-modal-aplicar");
    this.btnCancelModalAplicar = document.getElementById("btn-cancel-modal-aplicar");
    this.formConfirmarAplicacion = document.getElementById("form-confirmar-aplicacion");
    this.btnSubmitAplicar = document.getElementById("btn-submit-aplicar");
  }

  bindEvents() {
    // Drawer triggers
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

    // Modal Pasantía triggers
    if (this.btnAgregarPasantia) {
      this.btnAgregarPasantia.addEventListener("click", () => this.openModalCrear());
    }
    if (this.btnCloseModal) {
      this.btnCloseModal.addEventListener("click", () => this.closeModal());
    }
    if (this.btnCancelModal) {
      this.btnCancelModal.addEventListener("click", () => this.closeModal());
    }
    if (this.formAgregarPasantia) {
      this.formAgregarPasantia.addEventListener("submit", (e) => this.handleSubmitPasantia(e));
    }

    // Modal Postulantes triggers
    if (this.btnCloseModalPostulantes) {
      this.btnCloseModalPostulantes.addEventListener("click", () => this.closeModalPostulantes());
    }

    // Modal Aplicar Pasantía triggers
    if (this.btnCloseModalAplicar) {
      this.btnCloseModalAplicar.addEventListener("click", () => this.closeModalAplicar());
    }
    if (this.btnCancelModalAplicar) {
      this.btnCancelModalAplicar.addEventListener("click", () => this.closeModalAplicar());
    }
    if (this.formConfirmarAplicacion) {
      this.formConfirmarAplicacion.addEventListener("submit", (e) => this.handleSubmitConfirmarAplicacion(e));
    }

    // Logout
    if (this.btnDrawerLogout) {
      this.btnDrawerLogout.addEventListener("click", () => this.logout());
    }

    // Búsqueda con debounce
    if (this.searchInput) {
      let debounceTimer = null;
      this.searchInput.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          this.filters.search = e.target.value.trim();
          this.loadPasantias();
        }, 300);
      });
    }

    // Cerrar con Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.closeDrawer();
        this.closeModal();
        this.closeModalPostulantes();
        this.closeModalAplicar();
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 1. Autenticación y Carga de Perfil en Sesión (GET /api/auth/me)
  // ---------------------------------------------------------------------------
  async fetchCurrentUser() {
    try {
      const res = await fetch("/api/auth/me");
      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }
      const data = await res.json();
      if (data.success && data.user) {
        this.currentUser = data.user;
        const u = data.user;

        // Actualizar UI de usuario
        if (this.drawerUserName) this.drawerUserName.textContent = u.nombre_completo || u.username;
        if (this.drawerUserCup) this.drawerUserCup.textContent = u.cup ? `#CUP ${u.cup}` : `#ROL ${u.role}`;
        if (this.drawerUserEmail) this.drawerUserEmail.textContent = u.email;

        // Mostrar Badge de Rol en la barra superior
        if (this.topbarUserBadge) {
          this.topbarUserBadge.style.display = "inline-block";
          this.topbarUserBadge.textContent = u.role;
          if (u.role === "Estudiante") {
            this.topbarUserBadge.style.background = "#059669";
          } else if (u.role === "Supervisor") {
            this.topbarUserBadge.style.background = "#D97706";
          } else {
            this.topbarUserBadge.style.background = "#033E8C";
          }
        }

        // Habilitar botón de agregar pasantía solo si es Admin o Empresa
        if (u.role === "Administrador" || u.role === "Supervisor") {
          if (this.adminActionContainer) this.adminActionContainer.style.display = "flex";
        } else {
          if (this.adminActionContainer) this.adminActionContainer.style.display = "none";
        }

        // Habilitar accesos exclusivos para Administrador
        const btnTopbarUsuarios = document.getElementById("btn-topbar-admin-usuarios");
        const btnDrawerUsuarios = document.getElementById("btn-drawer-admin-usuarios");
        if (u.role === "Administrador") {
          if (btnTopbarUsuarios) btnTopbarUsuarios.style.display = "inline-flex";
          if (btnDrawerUsuarios) btnDrawerUsuarios.style.display = "inline-flex";
        } else {
          if (btnTopbarUsuarios) btnTopbarUsuarios.style.display = "none";
          if (btnDrawerUsuarios) btnDrawerUsuarios.style.display = "none";
        }

        // Cargar postulaciones o empresas según el rol
        await this.loadDrawerNotifications();
      }
    } catch (err) {
      console.warn("No se pudo verificar la sesión:", err);
    }
  }

  async logout() {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
    } catch (_) {}
    window.location.href = "/login";
  }

  // ---------------------------------------------------------------------------
  // 2. Lectura y Filtrado de Pasantías (GET /api/pasantias)
  // ---------------------------------------------------------------------------
  async loadPasantias() {
    const params = new URLSearchParams();
    if (this.filters.search) params.set("busqueda", this.filters.search);
    if (this.filters.modalidad) params.set("modalidad", this.filters.modalidad);
    if (this.filters.experiencia) params.set("experiencia", this.filters.experiencia);
    if (this.filters.sector) params.set("sector", this.filters.sector);
    if (this.filters.ciudad) params.set("ciudad", this.filters.ciudad);

    try {
      const res = await fetch(`/api/pasantias?${params.toString()}`);
      if (res.status === 401) {
        window.location.href = "/login";
        return;
      }
      const data = await res.json();
      if (data.success && Array.isArray(data.pasantias)) {
        this.pasantias = data.pasantias;
      } else {
        this.pasantias = [];
      }
    } catch (err) {
      console.error("Error al cargar pasantías desde la API:", err);
      this.pasantias = [];
    }

    // Si es estudiante, refrescar mapa de aplicaciones para marcar las tarjetas
    if (this.currentUser && this.currentUser.role === "Estudiante") {
      await this.refreshMisAplicacionesMap();
    }

    this.renderGrid();
  }

  async refreshMisAplicacionesMap() {
    try {
      const res = await fetch("/api/pasantias/mis-aplicaciones");
      if (res.ok) {
        const data = await res.json();
        if (data.success && Array.isArray(data.aplicaciones)) {
          this.misAplicaciones.clear();
          data.aplicaciones.forEach(app => {
            this.misAplicaciones.set(app.id_oferta, app);
          });
        }
      }
    } catch (_) {}
  }

  renderGrid() {
    if (!this.gridContainer) return;

    if (this.statusTextCount) {
      const cant = this.pasantias.length;
      this.statusTextCount.textContent = cant === 1 ? "1 Oferta Activa" : `${cant} Ofertas Activas`;
    }

    if (this.pasantias.length === 0) {
      this.gridContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: #64748B;">
          <i data-lucide="inbox" style="width: 48px; height: 48px; margin: 0 auto 12px; display: block; opacity: 0.5;"></i>
          <h4 style="font-size: 16px; font-weight: 600; color: #334155;">No se encontraron pasantías en la base de datos</h4>
          <p style="font-size: 13px;">Prueba ajustando los filtros de búsqueda o agrega una nueva pasantía.</p>
        </div>
      `;
      this.initLucideIcons();
      return;
    }

    const isStudent = this.currentUser && this.currentUser.role === "Estudiante";
    const canManage = this.currentUser && (this.currentUser.role === "Administrador" || this.currentUser.role === "Supervisor");

    this.gridContainer.innerHTML = this.pasantias.map(p => {
      const isExpanded = this.expandedCardId === p.id;
      const aplicacionPrevia = this.misAplicaciones.get(p.id);

      let studentActionHtml = "";
      if (isStudent) {
        if (aplicacionPrevia) {
          studentActionHtml = `
            <button type="button" class="btn-pasantia-guardar" style="background: #E2E8F0; color: #334155; cursor: default;" onclick="event.stopPropagation();">
              Postulado (${aplicacionPrevia.estado})
            </button>
          `;
        } else {
          studentActionHtml = `
            <button type="button" class="btn-pasantia-solicitar" onclick="event.stopPropagation(); window.pasantiasApp.solicitarPasantia(${p.id})">
              POSTULARME
            </button>
          `;
        }
      }

      let manageActionsHtml = "";
      if (canManage) {
        manageActionsHtml = `
          <button type="button" class="btn-pasantia-guardar" style="background: #033E8C; color: #FFF;" onclick="event.stopPropagation(); window.pasantiasApp.verPostulantes(${p.id}, '${p.titulo.replace(/'/g, "\\'")}')">
            POSTULANTES (${p.postulantes_count || 0})
          </button>
          <button type="button" class="btn-pasantia-guardar" style="background: #F1F5F9; color: #0F172A;" onclick="event.stopPropagation(); window.pasantiasApp.openModalEditar(${p.id})">
            EDITAR
          </button>
          <button type="button" class="btn-pasantia-guardar" style="background: #FEE2E2; color: #DC2626;" onclick="event.stopPropagation(); window.pasantiasApp.eliminarPasantia(${p.id})">
            ELIMINAR
          </button>
        `;
      }

      return `
        <div class="pasantia-card ${isExpanded ? 'is-expanded' : ''}" data-id="${p.id}" id="pasantia-card-${p.id}">
          <img src="/static/img/pasantia_banner.jpg" alt="Pasantía UNI" class="pasantia-card-banner" />
          <div class="pasantia-card-body">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
              <h3 class="pasantia-card-title">${p.titulo}</h3>
              <span style="font-size: 11px; font-weight: 700; color: #059669; background: #ECFDF5; padding: 2px 8px; border-radius: 12px; white-space: nowrap;">
                ${p.cupos || 1} plaza${(p.cupos || 1) > 1 ? 's' : ''}
              </span>
            </div>

            <div style="font-size: 12px; color: #475569; margin: 4px 0 8px 0; font-weight: 500;">
              Empresa: <strong>${p.empresa_nombre || 'Entidad Receptora UNI'}</strong> · ${p.ciudad || 'Managua'}
            </div>
            
            ${isExpanded ? `
              <div class="pasantia-badges-row">
                <span class="pasantia-badge">${p.tipo || 'Académica'}</span>
                <span class="pasantia-badge badge-presencial">${p.modalidad || 'Presencial'}</span>
                <span class="pasantia-badge">${p.duracion || '160H'}</span>
                <span class="pasantia-badge" style="background: #F8FAFC; border: 1px solid #CBD5E1;">${p.sector || 'General'}</span>
              </div>
            ` : ''}

            <span class="pasantia-card-desc-label">Descripción:</span>
            <p class="pasantia-card-desc-text">${p.descripcion || 'Sin descripción detallada disponible.'}</p>

            ${isExpanded && p.requisitos ? `
              <span class="pasantia-card-desc-label" style="margin-top: 6px;">Requisitos:</span>
              <p class="pasantia-card-desc-text" style="color: #334155; font-style: italic;">${p.requisitos}</p>
            ` : ''}

            ${isExpanded ? `
              <div class="pasantia-actions-row" style="flex-wrap: wrap; gap: 6px; margin-top: 12px;">
                ${studentActionHtml}
                ${manageActionsHtml}
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }).join("");

    // Asignar clic para expandir
    this.gridContainer.querySelectorAll(".pasantia-card").forEach(card => {
      card.addEventListener("click", () => {
        const id = parseInt(card.dataset.id, 10);
        this.toggleCardExpand(id);
      });
    });

    this.initLucideIcons();
  }

  toggleCardExpand(id) {
    this.expandedCardId = this.expandedCardId === id ? null : id;
    this.renderGrid();
  }

  // ---------------------------------------------------------------------------
  // 3. Postulación de Estudiantes con Checklist de Documentos (CU-03)
  // ---------------------------------------------------------------------------
  async solicitarPasantia(id) {
    const oferta = this.pasantias.find(p => p.id === id);
    if (!oferta) {
      this.showToast("No se encontró la oferta de pasantía seleccionada.", "error");
      return;
    }

    if (this.modalAplicarOfertaId) this.modalAplicarOfertaId.value = id;
    if (this.modalAplicarOfertaTitulo) this.modalAplicarOfertaTitulo.textContent = oferta.titulo || "Pasantía";
    if (this.modalAplicarOfertaEmpresa) {
      this.modalAplicarOfertaEmpresa.textContent = `Empresa: ${oferta.empresa_nombre || 'Entidad Receptora UNI'} · Modalidad: ${oferta.modalidad || 'Presencial'} · Duración: ${oferta.duracion || '160H'}`;
    }
    if (this.modalAplicarMotivo) this.modalAplicarMotivo.value = "";

    // Cargar documentos del estudiante para selección
    if (this.modalAplicarDocsContainer) {
      this.modalAplicarDocsContainer.innerHTML = `
        <div style="text-align: center; padding: 16px; color: #64748B; font-size: 13px;">
          Cargando tus documentos registrados...
        </div>
      `;
    }

    this.modalAplicar.classList.add("is-visible");
    this.initLucideIcons();

    try {
      const res = await fetch("/api/estudiantes/documentos");
      const data = await res.json();

      if (res.ok && data.success && Array.isArray(data.documentos) && data.documentos.length > 0) {
        this.modalAplicarDocsContainer.innerHTML = data.documentos.map(doc => {
          const tipoLegible = (doc.tipo_documento || 'Otro').replace(/_/g, ' ');
          return `
            <label style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; cursor: pointer; transition: background 0.15s ease;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <input type="checkbox" class="check-doc-autorizar" value="${doc.id}" checked style="width: 18px; height: 18px; accent-color: #033E8C; cursor: pointer;" />
                <div>
                  <span style="font-weight: 700; font-size: 13px; color: #0F172A; display: block;">
                    📄 ${tipoLegible}
                  </span>
                  <span style="font-size: 11px; color: #64748B;">
                    ${doc.nombre_original || 'documento'}
                  </span>
                </div>
              </div>
              <a href="${doc.ruta_archivo}" target="_blank" rel="noopener noreferrer" style="font-size: 11.5px; color: #033E8C; text-decoration: underline; font-weight: 600;" onclick="event.stopPropagation();">
                Visualizar
              </a>
            </label>
          `;
        }).join("");
      } else {
        this.modalAplicarDocsContainer.innerHTML = `
          <div style="padding: 14px; background: #FFFBEB; border: 1px solid #FCD34D; border-radius: 8px; color: #92400E; font-size: 12.5px; line-height: 1.5;">
            <strong>Aviso:</strong> No tienes documentos adjuntos en tu perfil (CV, récord policial, licencia, etc.). Puedes postularte directamente ahora y agregar tus documentos posteriormente desde <a href="/perfil" target="_blank" style="color: #1E3A8A; font-weight: 700; text-decoration: underline;">Mi Perfil</a>.
          </div>
        `;
      }
    } catch (_) {
      this.modalAplicarDocsContainer.innerHTML = `
        <div style="text-align: center; padding: 14px; color: #DC2626; font-size: 12.5px;">
          No se pudieron cargar tus documentos. Puedes proceder con la postulación.
        </div>
      `;
    }
  }

  closeModalAplicar() {
    this.modalAplicar?.classList.remove("is-visible");
    this.formConfirmarAplicacion?.reset();
  }

  async handleSubmitConfirmarAplicacion(e) {
    e.preventDefault();
    const id = this.modalAplicarOfertaId.value;
    if (!id) return;

    const checkedBoxes = this.modalAplicarDocsContainer?.querySelectorAll(".check-doc-autorizar:checked") || [];
    const documentosCompartidos = Array.from(checkedBoxes).map(cb => parseInt(cb.value, 10));
    const motivo = (this.modalAplicarMotivo?.value || "").trim() || "Postulación directa enviada desde el portal web de pasantías.";

    if (this.btnSubmitAplicar) {
      this.btnSubmitAplicar.disabled = true;
      this.btnSubmitAplicar.textContent = "Enviando postulación...";
    }

    try {
      const res = await fetch(`/api/pasantias/${id}/aplicar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          motivo_postulacion: motivo,
          documentos_compartidos: documentosCompartidos
        })
      });
      const data = await res.json();

      if (res.status === 201 && data.success) {
        this.showToast(data.message || "¡Postulación enviada exitosamente!", "success");
        this.closeModalAplicar();
        await this.loadPasantias();
        await this.loadDrawerNotifications();
      } else {
        // Mostrar mensaje detallado de validación académica (CU-01 / CU-09)
        this.showToast(data.message || "No cumples con los criterios para postularte a esta pasantía.", "error");
      }
    } catch (err) {
      this.showToast("Error de red al procesar la postulación.", "error");
    } finally {
      if (this.btnSubmitAplicar) {
        this.btnSubmitAplicar.disabled = false;
        this.btnSubmitAplicar.textContent = "Enviar Postulación Formal";
      }
    }
  }

  // ---------------------------------------------------------------------------
  // 4. Creación y Edición de Ofertas (POST/PUT /api/pasantias - CU-06)
  // ---------------------------------------------------------------------------
  openModalCrear() {
    this.formAgregarPasantia.reset();
    this.modalPasantiaId.value = "";
    this.modalPasantiaTitle.textContent = "Publicar Nueva Pasantía";
    this.modalPasantia.classList.add("is-visible");
  }

  async openModalEditar(id) {
    try {
      const res = await fetch(`/api/pasantias/${id}`);
      const data = await res.json();
      if (!res.ok || !data.success) {
        this.showToast("No se pudo obtener la información de la pasantía", "error");
        return;
      }
      const p = data.pasantia;
      this.modalPasantiaId.value = p.id;
      this.modalPasantiaTitle.textContent = `Editar Pasantía: ${p.titulo}`;
      document.getElementById("modal-pasantia-titulo").value = p.titulo || "";
      document.getElementById("modal-pasantia-tipo").value = p.tipo || "Académica";
      document.getElementById("modal-pasantia-modalidad").value = p.modalidad || "Presencial";
      document.getElementById("modal-pasantia-horas").value = p.duracion || "160H";
      document.getElementById("modal-pasantia-experiencia").value = p.experiencia || "Sin experiencia";
      document.getElementById("modal-pasantia-sector").value = p.sector || "Tecnología";
      document.getElementById("modal-pasantia-ciudad").value = p.ciudad || "Managua";
      document.getElementById("modal-pasantia-cupos").value = p.cupos || 1;
      document.getElementById("modal-pasantia-remuneracion").value = p.remunerada ? "Remunerada" : "No remunerada";
      document.getElementById("modal-pasantia-requisitos").value = p.requisitos || "";
      document.getElementById("modal-pasantia-desc").value = p.descripcion || "";

      this.modalPasantia.classList.add("is-visible");
    } catch (_) {
      this.showToast("Error al cargar datos para edición", "error");
    }
  }

  closeModal() {
    this.modalPasantia?.classList.remove("is-visible");
    this.formAgregarPasantia?.reset();
  }

  async handleSubmitPasantia(e) {
    e.preventDefault();
    const id = this.modalPasantiaId.value;
    const isEdit = Boolean(id);

    const payload = {
      titulo: document.getElementById("modal-pasantia-titulo").value.trim(),
      tipo: document.getElementById("modal-pasantia-tipo").value,
      modalidad: document.getElementById("modal-pasantia-modalidad").value,
      duracion: document.getElementById("modal-pasantia-horas").value.trim(),
      experiencia: document.getElementById("modal-pasantia-experiencia").value,
      sector: document.getElementById("modal-pasantia-sector").value,
      ciudad: document.getElementById("modal-pasantia-ciudad").value,
      cupos: parseInt(document.getElementById("modal-pasantia-cupos").value, 10) || 1,
      remunerada: document.getElementById("modal-pasantia-remuneracion").value === "Remunerada",
      requisitos: document.getElementById("modal-pasantia-requisitos").value.trim(),
      descripcion: document.getElementById("modal-pasantia-desc").value.trim(),
    };

    const url = isEdit ? `/api/pasantias/${id}` : "/api/pasantias";
    const method = isEdit ? "PUT" : "POST";

    try {
      const res = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (res.ok && data.success) {
        this.showToast(data.message || (isEdit ? "Pasantía actualizada" : "Pasantía creada"), "success");
        this.closeModal();
        await this.loadPasantias();
      } else {
        this.showToast(data.message || "Error al guardar en base de datos", "error");
      }
    } catch (err) {
      this.showToast("Error de comunicación con el servidor", "error");
    }
  }

  // ---------------------------------------------------------------------------
  // 5. Eliminación de Ofertas (DELETE /api/pasantias/<id>)
  // ---------------------------------------------------------------------------
  async eliminarPasantia(id) {
    if (!confirm("¿Confirmas la eliminación permanente de esta oferta de pasantía y sus postulaciones?")) {
      return;
    }

    try {
      const res = await fetch(`/api/pasantias/${id}`, { method: "DELETE" });
      const data = await res.json();
      if (res.ok && data.success) {
        this.showToast(data.message || "Oferta eliminada con éxito", "success");
        await this.loadPasantias();
      } else {
        this.showToast(data.message || "Error al eliminar oferta", "error");
      }
    } catch (_) {
      this.showToast("Error de red al intentar eliminar la oferta", "error");
    }
  }

  // ---------------------------------------------------------------------------
  // 6. Evaluación de Postulantes (GET/PUT /api/pasantias/<id>/aplicaciones - CU-07)
  // ---------------------------------------------------------------------------
  async verPostulantes(idOferta, tituloOferta) {
    this.modalPostulantesTitle.textContent = `Postulantes: ${tituloOferta}`;
    this.modalPostulantesBody.innerHTML = `
      <div style="text-align: center; padding: 24px; color: #64748B;">Cargando postulaciones desde la base de datos...</div>
    `;
    this.modalPostulantes.classList.add("is-visible");

    try {
      const res = await fetch(`/api/pasantias/${idOferta}/aplicaciones`);
      const data = await res.json();

      if (!res.ok || !data.success || !Array.isArray(data.aplicaciones) || data.aplicaciones.length === 0) {
        this.modalPostulantesBody.innerHTML = `
          <div style="text-align: center; padding: 30px; color: #64748B;">
            <p>Aún no hay estudiantes postulados para esta oferta de pasantía.</p>
          </div>
        `;
        return;
      }

      this.modalPostulantesBody.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 14px;">
          ${data.aplicaciones.map(app => {
            const cand = app.candidato || {};
            const docs = cand.documentos || app.documentos || [];
            return `
              <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; display: flex; flex-direction: column; gap: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap;">
                  <div>
                    <h4 style="margin: 0 0 4px 0; font-size: 15px; color: #0F172A; font-weight: 700;">
                      ${cand.nombre_completo || 'Estudiante Postulante'}
                    </h4>
                    <div style="font-size: 12px; color: #475569; display: flex; flex-wrap: wrap; gap: 8px;">
                      <span>CUP: <strong>${cand.cup || 'N/A'}</strong></span>
                      <span>·</span>
                      <span>Cédula: <strong>${cand.cedula || 'N/A'}</strong></span>
                      <span>·</span>
                      <span>${cand.carrera || 'Carrera afín'} (${cand.anio_academico || 4}° Año)</span>
                    </div>
                    <div style="font-size: 12px; color: #64748B; margin-top: 4px;">
                      Contacto: <strong>${cand.email || 'Sin correo'}</strong> ${cand.telefono_principal ? `· Tel: <strong>${cand.telefono_principal}</strong>` : ''}
                    </div>
                  </div>

                  <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 11.5px; font-weight: 700; padding: 4px 10px; border-radius: 12px; background: ${app.estado === 'Aceptado' ? '#DCFCE7' : app.estado === 'Rechazado' ? '#FEE2E2' : '#FEF3C7'}; color: ${app.estado === 'Aceptado' ? '#15803D' : app.estado === 'Rechazado' ? '#B91C1C' : '#B45309'};">
                      ${app.estado}
                    </span>
                    <div style="display: flex; gap: 6px;">
                      ${app.estado !== 'Aceptado' ? `
                        <button type="button" style="background: #059669; color: #fff; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;" onclick="window.pasantiasApp.cambiarEstadoPostulacion(${app.id_aplicacion}, 'Aceptado', ${idOferta}, '${tituloOferta.replace(/'/g, "\\'")}')">
                          Aceptar
                        </button>
                      ` : ''}
                      ${app.estado !== 'Rechazado' ? `
                        <button type="button" style="background: #DC2626; color: #fff; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;" onclick="window.pasantiasApp.cambiarEstadoPostulacion(${app.id_aplicacion}, 'Rechazado', ${idOferta}, '${tituloOferta.replace(/'/g, "\\'")}')">
                          Rechazar
                        </button>
                      ` : ''}
                    </div>
                  </div>
                </div>

                <!-- Documentos adjuntos del postulante (CV, Récord, Licencia, etc.) -->
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px 12px;">
                  <span style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 6px;">
                    Documentos y Expediente del Candidato (${docs.length}):
                  </span>
                  ${docs.length > 0 ? `
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                      ${docs.map(d => `
                        <a href="${d.ruta_archivo}" target="_blank" rel="noopener noreferrer" style="background: #EFF6FF; border: 1px solid #BFDBFE; color: #1D4ED8; padding: 5px 10px; border-radius: 6px; font-size: 11.5px; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                          <span>📄 ${d.tipo_documento.replace(/_/g, ' ')}</span>
                          <span style="color: #64748B; font-size: 10.5px;">(${d.nombre_original})</span>
                        </a>
                      `).join("")}
                    </div>
                  ` : `
                    <p style="margin: 0; font-size: 12px; color: #94A3B8; font-style: italic;">
                      El estudiante no ha adjuntado documentos (CV, récord policial, etc.) en su expediente aún.
                    </p>
                  `}
                </div>
              </div>
            `;
          }).join("")}
        </div>
      `;
    } catch (_) {
      this.modalPostulantesBody.innerHTML = `
        <div style="text-align: center; padding: 24px; color: #DC2626;">Error al consultar postulantes.</div>
      `;
    }
  }

  async cambiarEstadoPostulacion(idAplicacion, nuevoEstado, idOferta, tituloOferta) {
    try {
      const res = await fetch(`/api/pasantias/aplicaciones/${idAplicacion}/estado`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nuevo_estado: nuevoEstado })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        this.showToast(data.message || `Estado actualizado a ${nuevoEstado}`, "success");
        // Refrescar modal de postulantes
        await this.verPostulantes(idOferta, tituloOferta);
        await this.loadPasantias();
      } else {
        this.showToast(data.message || "Error al actualizar estado", "error");
      }
    } catch (_) {
      this.showToast("Error de red", "error");
    }
  }

  closeModalPostulantes() {
    this.modalPostulantes?.classList.remove("is-visible");
  }

  // ---------------------------------------------------------------------------
  // 7. Notificaciones Dinámicas en el Drawer Lateral
  // ---------------------------------------------------------------------------
  async loadDrawerNotifications() {
    if (!this.drawerNotificationsList || !this.currentUser) return;

    if (this.currentUser.role === "Estudiante") {
      this.drawerNotifHeading.textContent = "Mis Postulaciones Realizadas";
      try {
        const res = await fetch("/api/pasantias/mis-aplicaciones");
        const data = await res.json();
        if (res.ok && data.success && Array.isArray(data.aplicaciones) && data.aplicaciones.length > 0) {
          this.drawerNotificationsList.innerHTML = data.aplicaciones.map(app => `
            <div class="notification-card-item">
              <div class="notif-avatar-col">
                <div class="notif-avatar-circle"><i data-lucide="briefcase"></i></div>
              </div>
              <div class="notif-body-col">
                <h5 class="notif-title">${app.oferta_titulo || 'Pasantía'}</h5>
                <p class="notif-text">Empresa: ${app.empresa_nombre || 'UNI'} · Estado: <strong>${app.estado}</strong></p>
                <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">Enviado: ${app.created_at || 'Reciente'}</div>
              </div>
            </div>
          `).join("");
          this.initLucideIcons();
          return;
        }
      } catch (_) {}
      this.drawerNotificationsList.innerHTML = `
        <p style="color: #94A3B8; font-size: 12.5px; text-align: center; padding: 20px 0;">No tienes postulaciones activas en este momento.</p>
      `;
    } else if (this.currentUser.role === "Administrador") {
      this.drawerNotifHeading.textContent = "Empresas Pendientes de Validación";
      try {
        const res = await fetch("/api/empresas");
        const data = await res.json();
        if (res.ok && data.success && Array.isArray(data.empresas)) {
          const pendientes = data.empresas.filter(e => e.estado_aprobacion === "Pendiente_Aprobacion");
          if (pendientes.length > 0) {
            this.drawerNotificationsList.innerHTML = pendientes.map(emp => `
              <div class="notification-card-item">
                <div class="notif-avatar-col">
                  <div class="notif-avatar-circle"><i data-lucide="building"></i></div>
                </div>
                <div class="notif-body-col">
                  <h5 class="notif-title">${emp.nombre_comercial || emp.razon_social}</h5>
                  <p class="notif-text">Sector: ${emp.sector_economico || 'Empresarial'} · RUC: ${emp.ruc || 'N/A'}</p>
                  <div class="notif-buttons-row" style="margin-top: 8px;">
                    <button class="btn-notif-aceptar" onclick="window.pasantiasApp.aprobarEmpresa(${emp.id_entidad})">Aprobar</button>
                    <button class="btn-notif-vermas" style="background: #EF4444;" onclick="window.pasantiasApp.rechazarEmpresa(${emp.id_entidad})">Rechazar</button>
                  </div>
                </div>
              </div>
            `).join("");
            this.initLucideIcons();
            return;
          }
        }
      } catch (_) {}
      this.drawerNotificationsList.innerHTML = `
        <p style="color: #94A3B8; font-size: 12.5px; text-align: center; padding: 20px 0;">Todas las empresas registradas han sido validadas.</p>
      `;
    } else {
      this.drawerNotifHeading.textContent = "Notificaciones Institucionales";
      this.drawerNotificationsList.innerHTML = `
        <p style="color: #94A3B8; font-size: 12.5px; text-align: center; padding: 20px 0;">Sin notificaciones pendientes para tu rol.</p>
      `;
    }
  }

  async aprobarEmpresa(id) {
    try {
      const res = await fetch(`/api/empresas/${id}/aprobar`, { method: "PUT" });
      const data = await res.json();
      if (res.ok && data.success) {
        this.showToast(data.message || "Empresa aprobada exitosamente", "success");
        await this.loadDrawerNotifications();
        await this.loadPasantias();
      } else {
        this.showToast(data.message || "Error al aprobar empresa", "error");
      }
    } catch (_) {
      this.showToast("Error de conexión", "error");
    }
  }

  async rechazarEmpresa(id) {
    try {
      const res = await fetch(`/api/empresas/${id}/rechazar`, { method: "PUT" });
      const data = await res.json();
      if (res.ok && data.success) {
        this.showToast(data.message || "Empresa rechazada", "info");
        await this.loadDrawerNotifications();
      } else {
        this.showToast(data.message || "Error al rechazar empresa", "error");
      }
    } catch (_) {
      this.showToast("Error de conexión", "error");
    }
  }

  // ---------------------------------------------------------------------------
  // 8. Drawer UI & Filtros
  // ---------------------------------------------------------------------------
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
          const label = item.textContent.trim();
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
          this.loadPasantias();
        });
      });
    });

    document.addEventListener("click", () => {
      document.querySelectorAll(".filter-dropdown-menu.show").forEach(m => m.classList.remove("show"));
    });
  }

  initLucideIcons() {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
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
    toast.className = `toast-message toast-${type}`;
    toast.style.cssText = `
      background: ${type === 'success' ? '#059669' : type === 'error' ? '#DC2626' : '#033E8C'};
      color: #FFFFFF;
      padding: 12px 18px;
      border-radius: 8px;
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
      toast.style.transition = "all 0.25s ease";
      setTimeout(() => toast.remove(), 250);
    }, 3500);
  }
}

// Inicialización de la aplicación
window.pasantiasApp = new PasantiasApp();
