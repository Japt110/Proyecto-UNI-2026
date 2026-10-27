/* ==========================================================================
   UNI EVENTS PLATFORM - LÃ“GICA Y COMPORTAMIENTO INTERACTIVO (ES6 JS)
   ========================================================================== */

// Default Events Data (used if localStorage is empty)
const defaultEventsData = [
  {
    id: 1,
    title: "Proyectos cientÃ­ficos",
    status: "activos",
    tags: ["DACTIC", "FERIA"],
    date: "15 a 18 de Agosto, 2026",
    time: "08:00 AM - 04:00 PM",
    location: "Recinto Universitario Pedro ArÃ¡uz Palacios, Auditorio Central",
    image: "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80",
    description: "ExposiciÃ³n anual de proyectos de investigaciÃ³n cientÃ­fica de docentes y estudiantes en tecnologÃ­as de la informaciÃ³n.",
    coordinator: "Dr. Roberto Morales",
    capacity: "140 / 150 Asistentes"
  },
  {
    id: 2,
    title: "Proyectos cientÃ­ficos",
    status: "activos",
    tags: ["DACTIC", "FERIA"],
    date: "20 al 22 de Agosto, 2026",
    time: "09:00 AM - 03:00 PM",
    location: "Recinto Universitario SimÃ³n BolÃ­var, Laboratorio DACTIC",
    image: "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=600&q=80",
    description: "Feria de innovaciÃ³n robÃ³tica y desarrollo de software embebido aplicado a la industria nacional.",
    coordinator: "Ing. Maria Josefa PÃ©rez",
    capacity: "95 / 100 Asistentes"
  },
  {
    id: 3,
    title: "Proyectos cientÃ­ficos",
    status: "programados",
    tags: ["DACTIC", "FERIA"],
    date: "05 de Septiembre, 2026",
    time: "10:00 AM - 02:00 PM",
    location: "UNI Sede Norte, Sala de Concurrencia 2",
    image: "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=600&q=80",
    description: "Simposio sobre inteligencia artificial aplicada a la eficiencia energÃ©tica en construcciones civiles.",
    coordinator: "MSc. Alejandro Silva",
    capacity: "60 / 80 Registrados"
  },
  {
    id: 4,
    title: "Proyectos cientÃ­ficos",
    status: "programados",
    tags: ["DACTIC", "FERIA"],
    date: "12 de Septiembre, 2026",
    time: "08:30 AM - 05:00 PM",
    location: "Recinto Universitario SimÃ³n BolÃ­var, Plazoleta Central",
    image: "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=600&q=80",
    description: "Encuentro universitario de investigaciÃ³n ambiental y desarrollo sostenible.",
    coordinator: "Dra. Carmen LÃ³pez",
    capacity: "210 / 250 Registrados"
  },
  {
    id: 5,
    title: "Proyectos cientÃ­ficos",
    status: "programados",
    tags: ["DACTIC", "FERIA"],
    date: "25 de Septiembre, 2026",
    time: "09:00 AM - 12:00 PM",
    location: "Auditorio SalomÃ³n de la Selva",
    image: "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=600&q=80",
    description: "Taller prÃ¡ctico sobre arquitectura limpia y diseÃ±o estructural de vanguardia.",
    coordinator: "Ing. Carlos Mendoza",
    capacity: "45 / 50 Registrados"
  },
  {
    id: 6,
    title: "Proyectos cientÃ­ficos",
    status: "pasados",
    tags: ["DACTIC", "FERIA"],
    date: "10 de Julio, 2026",
    time: "08:00 AM - 04:00 PM",
    location: "Recinto Universitario Pedro ArÃ¡uz Palacios",
    image: "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600&q=80",
    description: "PresentaciÃ³n final de trabajos de grado de la cohorte 2026-I.",
    coordinator: "Decanato de IngenierÃ­a",
    capacity: "300 Asistentes (Finalizado)"
  },
  {
    id: 7,
    title: "Proyectos cientÃ­ficos",
    status: "pasados",
    tags: ["DACTIC", "FERIA"],
    date: "02 de Junio, 2026",
    time: "09:00 AM - 01:00 PM",
    location: "Biblioteca Central UNI",
    image: "https://images.unsplash.com/photo-1515187029135-18ee286d815b?auto=format&fit=crop&w=600&q=80",
    description: "Conferencia de telecomunicaciones y redes de alta velocidad.",
    coordinator: "Dpto. de ElectrÃ³nica",
    capacity: "180 Asistentes (Finalizado)"
  },
  {
    id: 8,
    title: "Proyectos cientÃ­ficos",
    status: "pasados",
    tags: ["DACTIC", "FERIA"],
    date: "18 de Mayo, 2026",
    time: "10:00 AM - 03:00 PM",
    location: "Recinto Universitario SimÃ³n BolÃ­var",
    image: "https://images.unsplash.com/photo-1531545514256-b1400bc00f31?auto=format&fit=crop&w=600&q=80",
    description: "Feria de proyectos comunitarios e innovaciÃ³n social universitaria.",
    coordinator: "ExtensiÃ³n Universitaria",
    capacity: "250 Asistentes (Finalizado)"
  }
];

// Carga eventos exclusivamente desde la API (con caché de sesión via ClientCache).
// El sistema localStorage anterior fue reemplazado por ClientCache + sessionStorage.
async function getEventsData() {
  if (typeof API !== "undefined" && API.getEventos) {
    try {
      const apiEvents = await API.getEventos();
      if (Array.isArray(apiEvents) && apiEvents.length > 0) {
        return apiEvents;
      }
    } catch (e) {
      console.warn("Error de red al consultar API.getEventos", e);
    }
  }
  // Si la API no responde, retornar array vacío en lugar de datos corruptos de localStorage
  return [];
}

let carouselPages = { activos: 0, programados: 0, pasados: 0 };
let chartInstances = {};
let currentUploadedCoverUrl = null;
let currentUploadedCoverFile = null;
let currentDetailCoverFile = null;

// DOM Initialization
document.addEventListener("DOMContentLoaded", async () => {
  // Limpiar datos legados del sistema de caché anterior (localStorage)
  try { localStorage.removeItem("uni_events_data"); } catch (_) { }

  if (window.lucide) {
    lucide.createIcons();
  }

  const currentPath = (window.location.pathname || "").toLowerCase();
  const isLoginPage = currentPath.endsWith("/login") || currentPath.endsWith("/login.html") || currentPath.endsWith("login.html");
  const currentPageRole = document.body.getAttribute("data-page");

  // Ocultar la página mientras se verifica la sesión (evita flash de contenido sin autenticar)
  if (!isLoginPage) {
    document.documentElement.style.visibility = "hidden";
  }

  if (typeof API !== "undefined" && API.getCurrentUser) {
    try {
      // ── PRECARGA PARALELA ─────────────────────────────────────────────────────
      // Lanzar auth y datos de la página al mismo tiempo para eliminar la espera
      // secuencial. La función de precarga solo lanza el fetch; la renderización
      // ocurre después de confirmar la sesión con los datos ya en caché.
      let prefetchFn = null;
      if (!isLoginPage) {
        if (currentPageRole === "encargado") {
          prefetchFn = () => API.getEventos();              // prefetch eventos
        } else if (currentPageRole === "rector") {
          prefetchFn = () => API.getStatsGlobales();        // prefetch stats globales
        } else if (currentPageRole === "detalle") {
          const params = new URLSearchParams(window.location.search);
          const id = params.get("id");
          if (id) prefetchFn = () => Promise.all([API.getEventoById(id), API.getCatalogos()]); // prefetch evento + catálogos
        } else if (currentPageRole === "crear") {
          prefetchFn = () => API.getCatalogos();            // prefetch catálogos
        }
      }

      // Lanzar auth y precarga en paralelo
      const [user] = await Promise.all([
        API.getCurrentUser(),
        prefetchFn ? prefetchFn().catch(() => null) : Promise.resolve(null)
      ]);

      if (user) {
        if (isLoginPage) {
          const targetUrl = user.role === "Rector" ? "rector.html" : "index.html";
          window.location.replace(targetUrl);
          return;
        }

        // Proteger página de rectoría de roles no autorizados
        const isRectorPage = currentPath.endsWith("/rector") || currentPath.endsWith("/rector.html") || currentPath.endsWith("rector.html");
        if (isRectorPage && user.role !== "Rector") {
          window.location.replace("index.html");
          return;
        }

        // Ocultar links de rector.html si no es Rector
        if (user.role !== "Rector") {
          document.querySelectorAll("a[href='rector.html']").forEach(el => {
            el.style.display = "none";
          });
        }

        // Mostrar la página: auth confirmada, datos ya están en caché por la precarga paralela
        document.documentElement.style.visibility = "visible";

        const userRoleEl = document.querySelector(".drawer-user-role");
        const userNameEl = document.querySelector(".drawer-user-name");
        const userEmailEl = document.querySelector(".drawer-email");
        if (userRoleEl) userRoleEl.textContent = user.role || "Usuario";
        if (userNameEl) userNameEl.textContent = user.email ? (user.email.split('@')[0].replace('.', ' ').toUpperCase()) : "Usuario UNI";
        if (userEmailEl) userEmailEl.textContent = user.email || "usuario@uni.edu.ni";

      } else {
        if (!isLoginPage) {
          window.location.replace("login.html");
          return;
        }
      }
    } catch (e) {
      if (!isLoginPage) {
        window.location.replace("login.html");
        return;
      }
    }
  }

  // ── RENDERIZADO ──────────────────────────────────────────────────────────────
  // Los datos ya están en caché gracias a la precarga paralela.
  // getEventos() / getStatsGlobales() / getEventoById() devuelven caché inmediata.
  if (currentPageRole === "rector") {
    await initCharts();
  } else if (currentPageRole === "encargado") {
    await renderAllCarousels();
  } else if (currentPageRole === "detalle") {
    await initDetailPage();
  } else if (currentPageRole === "crear") {
    await initCrearActividadPage();
  }


  // Drawer event listeners (vincular a cualquier elemento gatillo del perfil)
  const userProfileTriggers = document.querySelectorAll("#user-profile-trigger, .user-profile-trigger, .header-right, .topbar-profile");
  const btnCloseDrawer = document.getElementById("btn-close-drawer");
  const drawerBackdrop = document.getElementById("drawer-backdrop");

  userProfileTriggers.forEach(el => {
    el.style.cursor = "pointer";
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      openDrawer();
    });
  });

  if (btnCloseDrawer) btnCloseDrawer.addEventListener("click", closeDrawer);
  if (drawerBackdrop) drawerBackdrop.addEventListener("click", closeDrawer);

  // Cerrar Sesión — interceptar el <a class="item-logout"> en cualquier página
  // para destruir la sesión del servidor, limpiar el caché del cliente y redirigir.
  const logoutLink = document.querySelector(".item-logout");
  if (logoutLink) {
    logoutLink.addEventListener("click", async (e) => {
      e.preventDefault(); // Cancelar la navegación directa del href
      try {
        if (typeof API !== "undefined" && API.logout) {
          await API.logout(); // Destruye la sesión Flask + limpia ClientCache
        }
      } catch (_) {
        // Aunque el servidor falle, limpiar el caché local igualmente
        if (typeof ClientCache !== "undefined") ClientCache.invalidateAll();
      } finally {
        window.location.replace("/login"); // replace() evita volver atrás con el botón Back
      }
    });
  }

  // Search Input Listener
  const searchInput = document.getElementById("search-input");
  if (searchInput) {
    searchInput.addEventListener("input", handleSearchAndFilter);
  }

  // Filter Selects Listener
  document.querySelectorAll(".filter-select").forEach(select => {
    select.addEventListener("change", handleSearchAndFilter);
  });
});

/* ==========================================================================
   CHARTS INITIALIZATION
   ========================================================================== */
function initCharts() {
  const chartColors = {
    blue: "#4A7CF6",
    purple: "#A17CF3",
    orange: "#F8B179",
    yellow: "#FFDD67",
    green: "#34D399",
    teal: "#2DD4BF",
    indigo: "#818CF8"
  };

  // Helper functions
  function getEventRecinto(evt) {
    if (evt.recinto) return evt.recinto;
    const loc = (evt.location || "").toLowerCase();
    if (loc.includes("pedro") || loc.includes("rupap")) return "RUPAP";
    if (loc.includes("bolivar") || loc.includes("bolÃ­var") || loc.includes("rusb") || loc.includes("salomon") || loc.includes("salomÃ³n") || loc.includes("biblioteca")) return "RUSB";
    if (loc.includes("norte")) return "UNI Sede Norte";
    return "RUPAP";
  }

  function getEventMonthAndWeek(evt) {
    const dateStr = (evt.date || "").toLowerCase();
    let month = "Otro";
    if (dateStr.includes("enero")) month = "Enero";
    else if (dateStr.includes("febrero")) month = "Febrero";
    else if (dateStr.includes("marzo")) month = "Marzo";
    else if (dateStr.includes("abril")) month = "Abril";
    else if (dateStr.includes("mayo")) month = "Mayo";
    else if (dateStr.includes("junio")) month = "Junio";
    else if (dateStr.includes("julio")) month = "Julio";
    else if (dateStr.includes("agosto")) month = "Agosto";
    else if (dateStr.includes("septiembre")) month = "Septiembre";
    else if (dateStr.includes("octubre")) month = "Octubre";
    else if (dateStr.includes("noviembre")) month = "Noviembre";
    else if (dateStr.includes("diciembre")) month = "Diciembre";

    const numbers = dateStr.match(/\d+/g);
    let week = "Semana 1";
    if (numbers && numbers.length > 0) {
      const day = parseInt(numbers[0], 10);
      if (day <= 7) week = "Semana 1";
      else if (day <= 14) week = "Semana 2";
      else if (day <= 21) week = "Semana 3";
      else week = "Semana 4";
    }
    return { month, week };
  }

  function getAggregatedStats(events) {
    const totalEvents = events.length;
    if (totalEvents === 0) {
      return {
        rol: { estudiantes: 0, docentes: 0, admin: 0, visitantes: 0 },
        genero: { mujeres: 0, hombres: 0 },
        facultades: [0, 0, 0, 0, 0],
        edades: [0, 0, 0, 0, 0, 0],
        capacidades: { naturales: 0, discapacidad: 0, deficiencias: 0 },
        nacionalidad: { nacionales: 0, extranjeros: 0 },
        laboral: { soloEstudian: 0, trabajan: 0 },
        relacion: { solteros: 0, enRelacion: 0 },
        etnias: { mestizos: 0, miskitos: 0, criollos: 0, otras: 0 },
        procedencia: { urbano: 0, rural: 0 },
        formacion: { bachillerato: 0, ingenieria: 0, doctorado: 0, licenciatura: 0 },
        areaConocimiento: { educacion: 0, artes: 0, tecnologia: 0, informacion: 0 }
      };
    }

    const aggregated = {
      rol: { estudiantes: 0, docentes: 0, admin: 0, visitantes: 0 },
      genero: { mujeres: 0, hombres: 0 },
      facultades: [0, 0, 0, 0, 0],
      edades: [0, 0, 0, 0, 0, 0],
      capacidades: { naturales: 0, discapacidad: 0, deficiencias: 0 },
      nacionalidad: { nacionales: 0, extranjeros: 0 },
      laboral: { soloEstudian: 0, trabajan: 0 },
      relacion: { solteros: 0, enRelacion: 0 },
      etnias: { mestizos: 0, miskitos: 0, criollos: 0, otras: 0 },
      procedencia: { urbano: 0, rural: 0 },
      formacion: { bachillerato: 0, ingenieria: 0, doctorado: 0, licenciatura: 0 },
      areaConocimiento: { educacion: 0, artes: 0, tecnologia: 0, informacion: 0 }
    };

    events.forEach(evt => {
      const seed = typeof evt.id === "number" ? evt.id : 1;
      const stats = evt.stats || generateMockStats(seed);

      aggregated.rol.estudiantes += stats.rol.estudiantes;
      aggregated.rol.docentes += stats.rol.docentes;
      aggregated.rol.admin += stats.rol.admin;
      aggregated.rol.visitantes += stats.rol.visitantes;

      aggregated.genero.mujeres += stats.genero.mujeres;
      aggregated.genero.hombres += stats.genero.hombres;

      for (let i = 0; i < 5; i++) aggregated.facultades[i] += stats.facultades[i] || 0;
      for (let i = 0; i < 6; i++) aggregated.edades[i] += stats.edades[i] || 0;

      aggregated.capacidades.naturales += stats.capacidades.naturales;
      aggregated.capacidades.discapacidad += stats.capacidades.discapacidad;
      aggregated.capacidades.deficiencias += stats.capacidades.deficiencias;

      aggregated.nacionalidad.nacionales += stats.nacionalidad.nacionales;
      aggregated.nacionalidad.extranjeros += stats.nacionalidad.extranjeros;

      aggregated.laboral.soloEstudian += stats.laboral.soloEstudian;
      aggregated.laboral.trabajan += stats.laboral.trabajan;

      aggregated.relacion.solteros += stats.relacion.solteros;
      aggregated.relacion.enRelacion += stats.relacion.enRelacion;

      aggregated.etnias.mestizos += stats.etnias.mestizos;
      aggregated.etnias.miskitos += stats.etnias.miskitos;
      aggregated.etnias.criollos += stats.etnias.criollos;
      aggregated.etnias.otras += stats.etnias.otras;

      aggregated.procedencia.urbano += stats.procedencia.urbano;
      aggregated.procedencia.rural += stats.procedencia.rural;

      aggregated.formacion.bachillerato += stats.formacion.bachillerato;
      aggregated.formacion.ingenieria += stats.formacion.ingenieria;
      aggregated.formacion.doctorado += stats.formacion.doctorado;
      aggregated.formacion.licenciatura += stats.formacion.licenciatura;

      aggregated.areaConocimiento.educacion += stats.areaConocimiento.educacion;
      aggregated.areaConocimiento.artes += stats.areaConocimiento.artes;
      aggregated.areaConocimiento.tecnologia += stats.areaConocimiento.tecnologia;
      aggregated.areaConocimiento.informacion += stats.areaConocimiento.informacion;
    });

    // Averages
    aggregated.rol.estudiantes = Math.round(aggregated.rol.estudiantes / totalEvents);
    aggregated.rol.docentes = Math.round(aggregated.rol.docentes / totalEvents);
    aggregated.rol.admin = Math.round(aggregated.rol.admin / totalEvents);
    aggregated.rol.visitantes = Math.round(aggregated.rol.visitantes / totalEvents);

    aggregated.genero.mujeres = Math.round(aggregated.genero.mujeres / totalEvents);
    aggregated.genero.hombres = Math.round(aggregated.genero.hombres / totalEvents);

    for (let i = 0; i < 5; i++) aggregated.facultades[i] = Math.round(aggregated.facultades[i] / totalEvents);
    for (let i = 0; i < 6; i++) aggregated.edades[i] = Math.round(aggregated.edades[i] / totalEvents);

    aggregated.capacidades.naturales = Math.round(aggregated.capacidades.naturales / totalEvents);
    aggregated.capacidades.discapacidad = Math.round(aggregated.capacidades.discapacidad / totalEvents);
    aggregated.capacidades.deficiencias = Math.round(aggregated.capacidades.deficiencias / totalEvents);

    aggregated.nacionalidad.nacionales = Math.round(aggregated.nacionalidad.nacionales / totalEvents);
    aggregated.nacionalidad.extranjeros = Math.round(aggregated.nacionalidad.extranjeros / totalEvents);

    aggregated.laboral.soloEstudian = Math.round(aggregated.laboral.soloEstudian / totalEvents);
    aggregated.laboral.trabajan = Math.round(aggregated.laboral.trabajan / totalEvents);

    aggregated.relacion.solteros = Math.round(aggregated.relacion.solteros / totalEvents);
    aggregated.relacion.enRelacion = Math.round(aggregated.relacion.enRelacion / totalEvents);

    aggregated.etnias.mestizos = Math.round(aggregated.etnias.mestizos / totalEvents);
    aggregated.etnias.miskitos = Math.round(aggregated.etnias.miskitos / totalEvents);
    aggregated.etnias.criollos = Math.round(aggregated.etnias.criollos / totalEvents);
    aggregated.etnias.otras = Math.round(aggregated.etnias.otras / totalEvents);

    aggregated.procedencia.urbano = Math.round(aggregated.procedencia.urbano / totalEvents);
    aggregated.procedencia.rural = Math.round(aggregated.procedencia.rural / totalEvents);

    aggregated.formacion.bachillerato = Math.round(aggregated.formacion.bachillerato / totalEvents);
    aggregated.formacion.ingenieria = Math.round(aggregated.formacion.ingenieria / totalEvents);
    aggregated.formacion.doctorado = Math.round(aggregated.formacion.doctorado / totalEvents);
    aggregated.formacion.licenciatura = Math.round(aggregated.formacion.licenciatura / totalEvents);

    aggregated.areaConocimiento.educacion = Math.round(aggregated.areaConocimiento.educacion / totalEvents);
    aggregated.areaConocimiento.artes = Math.round(aggregated.areaConocimiento.artes / totalEvents);
    aggregated.areaConocimiento.tecnologia = Math.round(aggregated.areaConocimiento.tecnologia / totalEvents);
    aggregated.areaConocimiento.informacion = Math.round(aggregated.areaConocimiento.informacion / totalEvents);

    return aggregated;
  }

  // Update logic
  async function updateRectorDashboard() {
    const rawEvents = await getEventsData();
    const events = Array.isArray(rawEvents) ? rawEvents : [];
    const searchVal = document.getElementById("rector-search-input").value.trim().toLowerCase();
    const recintoVal = document.getElementById("rector-recinto-select").value;
    const monthVal = document.getElementById("rector-month-select").value;
    const weekVal = document.getElementById("rector-week-select").value;

    // Filter events
    let filtered = events.filter(evt => {
      // 1. Search term
      if (searchVal && !evt.title.toLowerCase().includes(searchVal)) {
        return false;
      }
      // 2. Recinto
      if (recintoVal !== "Todos") {
        if (getEventRecinto(evt) !== recintoVal) return false;
      }
      // 3. Month & Week
      const dateInfo = getEventMonthAndWeek(evt);
      if (monthVal !== "Todos" && dateInfo.month !== monthVal) return false;
      if (weekVal !== "Todos" && dateInfo.week !== weekVal) return false;

      return true;
    });

    const isSingleEventView = filtered.length === 1 && searchVal !== "";
    const bannerEl = document.getElementById("rector-general-events-banner");
    const countEl = document.getElementById("rector-event-count");
    const titleEl = document.querySelector(".statistics-title");

    let statsData;
    let apiGlobalStats = null;

    if (isSingleEventView) {
      // Single event stats
      const evt = filtered[0];
      const seed = typeof evt.id === "number" ? evt.id : 1;
      statsData = evt.stats || generateMockStats(seed);

      bannerEl.classList.add("hidden");
      titleEl.textContent = `Estadísticas - ${evt.title}`;
    } else {
      // Aggregated stats
      statsData = getAggregatedStats(filtered);

      if (typeof API !== "undefined" && API.getStatsGlobales) {
        apiGlobalStats = await API.getStatsGlobales(recintoVal !== "Todos" ? recintoVal : "");
        if (apiGlobalStats && apiGlobalStats.resumen) {
          countEl.textContent = apiGlobalStats.resumen.total_eventos;
        } else {
          countEl.textContent = filtered.length;
        }
      } else {
        countEl.textContent = filtered.length;
      }

      bannerEl.classList.remove("hidden");

      const recintoLabel = recintoVal === "Todos" ? "Todos los Recintos" : recintoVal;
      titleEl.textContent = `Estadísticas Generales - ${recintoLabel}`;
    }

    // Render Charts
    renderCharts(statsData, apiGlobalStats);
  }

  // Chart rendering
  function renderCharts(stats, apiGlobalStats = null) {
    const chartOpts = (extra = {}) => ({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: "bottom",
          labels: { color: "#374151", font: { size: 10, family: "Inter" }, boxWidth: 12, padding: 8 }
        }
      },
      ...extra
    });

    // Destroy existing instances to prevent overlap issues
    Object.keys(chartInstances).forEach(key => {
      if (chartInstances[key]) {
        chartInstances[key].destroy();
      }
    });

    // 1. Formacion (Doughnut)
    const ctxFormacion = document.getElementById("chart-formacion");
    if (ctxFormacion) {
      chartInstances.formacion = new Chart(ctxFormacion, {
        type: "doughnut",
        data: {
          labels: [
            `Bachillerato ${stats.formacion.bachillerato}%`,
            `Ingeniería ${stats.formacion.ingenieria}%`,
            `Doctorado ${stats.formacion.doctorado}%`,
            `Licenciatura ${stats.formacion.licenciatura}%`
          ],
          datasets: [{
            data: [stats.formacion.bachillerato, stats.formacion.ingenieria, stats.formacion.doctorado, stats.formacion.licenciatura],
            backgroundColor: [chartColors.blue, chartColors.purple, chartColors.orange, chartColors.yellow],
            borderWidth: 0
          }]
        },
        options: { ...chartOpts(), cutout: "55%" }
      });
    }

    // 2. Sexo (Pie)
    const ctxSexo = document.getElementById("chart-sexo");
    if (ctxSexo) {
      chartInstances.sexo = new Chart(ctxSexo, {
        type: "pie",
        data: {
          labels: [`Hombres ${stats.genero.hombres}%`, `Mujeres ${stats.genero.mujeres}%`],
          datasets: [{
            data: [stats.genero.hombres, stats.genero.mujeres],
            backgroundColor: [chartColors.blue, chartColors.purple],
            borderWidth: 0
          }]
        },
        options: chartOpts()
      });
    }

    // 3. Area (Doughnut)
    const ctxArea = document.getElementById("chart-area-conocimiento");
    if (ctxArea) {
      chartInstances.area = new Chart(ctxArea, {
        type: "doughnut",
        data: {
          labels: [
            `Educación ${stats.areaConocimiento.educacion}%`,
            `Artes y Hum. ${stats.areaConocimiento.artes}%`,
            `Tecnología ${stats.areaConocimiento.tecnologia}%`,
            `Información ${stats.areaConocimiento.informacion}%`
          ],
          datasets: [{
            data: [stats.areaConocimiento.educacion, stats.areaConocimiento.artes, stats.areaConocimiento.tecnologia, stats.areaConocimiento.informacion],
            backgroundColor: [chartColors.blue, chartColors.purple, chartColors.orange, chartColors.yellow],
            borderWidth: 0
          }]
        },
        options: { ...chartOpts(), cutout: "40%" }
      });
    }

    // 4. Rol (Doughnut)
    const ctxRol = document.getElementById("chart-rol-institucional");
    if (ctxRol) {
      chartInstances.rol = new Chart(ctxRol, {
        type: "doughnut",
        data: {
          labels: [
            `Estudiantes ${stats.rol.estudiantes}%`,
            `Docentes ${stats.rol.docentes}%`,
            `Admin. ${stats.rol.admin}%`,
            `Visitantes ${stats.rol.visitantes}%`
          ],
          datasets: [{
            data: [stats.rol.estudiantes, stats.rol.docentes, stats.rol.admin, stats.rol.visitantes],
            backgroundColor: [chartColors.blue, chartColors.purple, chartColors.orange, chartColors.yellow],
            borderWidth: 0
          }]
        },
        options: { ...chartOpts(), cutout: "55%" }
      });
    }

    // 5. Dirección Académica (Bar)
    const ctxDir = document.getElementById("chart-direccion-academica");
    if (ctxDir) {
      chartInstances.dir = new Chart(ctxDir, {
        type: "bar",
        data: {
          labels: ["DACTIC", "Ingeniería", "Arquitectura", "Ciencias", "DACTIC II"],
          datasets: [{
            label: "Asistentes",
            data: stats.facultades,
            backgroundColor: [chartColors.blue, chartColors.purple, chartColors.orange, chartColors.yellow, chartColors.teal],
            borderRadius: 6, borderWidth: 0
          }]
        },
        options: {
          ...chartOpts({ plugins: { legend: { display: false } } }),
          scales: {
            x: { ticks: { color: "#4B5563", font: { size: 9, family: "Inter" } }, grid: { color: "rgba(0,0,0,0.05)" } },
            y: { ticks: { color: "#4B5563", font: { size: 9, family: "Inter" } }, grid: { color: "rgba(0,0,0,0.05)" } }
          }
        }
      });
    }

    // 6. Edades (Bar)
    const ctxEdades = document.getElementById("chart-edades");
    if (ctxEdades) {
      chartInstances.edades = new Chart(ctxEdades, {
        type: "bar",
        data: {
          labels: ["17-19", "20-22", "23-25", "26-30", "31-40", "41+"],
          datasets: [{
            label: "Personas",
            data: stats.edades,
            backgroundColor: chartColors.teal,
            borderRadius: 5, borderWidth: 0
          }]
        },
        options: {
          ...chartOpts({ plugins: { legend: { display: false } } }),
          scales: {
            x: { ticks: { color: "#4B5563", font: { size: 9, family: "Inter" } }, grid: { display: false } },
            y: { ticks: { color: "#4B5563", font: { size: 9, family: "Inter" } }, grid: { color: "rgba(0,0,0,0.05)" } }
          }
        }
      });
    }

    // 7. Origen (Pie)
    const ctxNac = document.getElementById("chart-nacionalidad");
    if (ctxNac) {
      chartInstances.nac = new Chart(ctxNac, {
        type: "pie",
        data: {
          labels: [`Nacionales ${stats.nacionalidad.nacionales}%`, `Extranjeros ${stats.nacionalidad.extranjeros}%`],
          datasets: [{
            data: [stats.nacionalidad.nacionales, stats.nacionalidad.extranjeros],
            backgroundColor: [chartColors.blue, chartColors.orange],
            borderWidth: 0
          }]
        },
        options: chartOpts()
      });
    }

    // 8. Etnias (Doughnut)
    const ctxEtnias = document.getElementById("chart-etnias");
    if (ctxEtnias) {
      chartInstances.etnias = new Chart(ctxEtnias, {
        type: "doughnut",
        data: {
          labels: [
            `Mestizos ${stats.etnias.mestizos}%`,
            `Miskitos ${stats.etnias.miskitos}%`,
            `Criollos ${stats.etnias.criollos}%`,
            `Otras ${stats.etnias.otras}%`
          ],
          datasets: [{
            data: [stats.etnias.mestizos, stats.etnias.miskitos, stats.etnias.criollos, stats.etnias.otras],
            backgroundColor: [chartColors.blue, chartColors.green, chartColors.yellow, chartColors.purple],
            borderWidth: 0
          }]
        },
        options: { ...chartOpts(), cutout: "50%" }
      });
    }

    // 9. Procedencia (Pie)
    const ctxProc = document.getElementById("chart-procedencia");
    if (ctxProc) {
      chartInstances.proc = new Chart(ctxProc, {
        type: "pie",
        data: {
          labels: [`Urbano ${stats.procedencia.urbano}%`, `Rural ${stats.procedencia.rural}%`],
          datasets: [{
            data: [stats.procedencia.urbano, stats.procedencia.rural],
            backgroundColor: [chartColors.indigo, chartColors.green],
            borderWidth: 0
          }]
        },
        options: chartOpts()
      });
    }

    // 13. Impacto Estrategia Nacional 2026 (Doughnut)
    const ctxEjes = document.getElementById("chart-ejes-2026");
    if (ctxEjes) {
      const ejesData = apiGlobalStats && apiGlobalStats.ejes_estrategicos ? apiGlobalStats.ejes_estrategicos : {
        "Eje 1: Educación de Calidad": 6,
        "Eje 2: Ciencia, Tecnología e Innovación": 8,
        "Eje 3: Desarrollo Sostenible": 4
      };
      const ejesLabels = Object.keys(ejesData);
      const ejesValues = Object.values(ejesData);

      chartInstances.ejes2026 = new Chart(ctxEjes, {
        type: "doughnut",
        data: {
          labels: ejesLabels,
          datasets: [{
            data: ejesValues,
            backgroundColor: [chartColors.blue, chartColors.purple, chartColors.green, chartColors.orange],
            borderWidth: 0
          }]
        },
        options: { ...chartOpts(), cutout: "50%" }
      });
    }

    // 14. Estudiantes vs Trabajadores (Bar)
    const ctxTipoPersona = document.getElementById("chart-tipo-persona");
    if (ctxTipoPersona) {
      const comp = apiGlobalStats && apiGlobalStats.composicion_personas ? apiGlobalStats.composicion_personas : {
        estudiantes: 450, trabajadores: 120, otros: 30
      };

      chartInstances.tipoPersona = new Chart(ctxTipoPersona, {
        type: "bar",
        data: {
          labels: ["Estudiantes", "Trabajadores / Docentes", "Otros / Visitantes"],
          datasets: [{
            label: "Asistentes Registrados",
            data: [comp.estudiantes || 0, comp.trabajadores || 0, comp.otros || 0],
            backgroundColor: [chartColors.blue, chartColors.orange, chartColors.teal],
            borderRadius: 6, borderWidth: 0
          }]
        },
        options: {
          ...chartOpts({ plugins: { legend: { display: false } } }),
          scales: {
            x: { ticks: { color: "#4B5563", font: { size: 9, family: "Inter" } }, grid: { display: false } },
            y: { ticks: { color: "#4B5563", font: { size: 9, family: "Inter" } }, grid: { color: "rgba(0,0,0,0.05)" }, beginAtZero: true }
          }
        }
      });
    }

    // 10. Text stats (Capacidades, Laboral, Relacion) - Elementos opcionales
    const setElemText = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    if (stats && stats.capacidades) {
      setElemText("stat-naturales", (stats.capacidades.naturales || 0) + "%");
      setElemText("stat-discapacidad", (stats.capacidades.discapacidad || 0) + "%");
      setElemText("stat-deficiencias", (stats.capacidades.deficiencias || 0) + "%");
    }

    if (stats && stats.laboral) {
      setElemText("stat-solo-estudian", (stats.laboral.soloEstudian || 0) + "%");
      setElemText("stat-trabajan", (stats.laboral.trabajan || 0) + "%");
    }

    if (stats && stats.relacion) {
      setElemText("stat-solteros", (stats.relacion.solteros || 0) + "%");
      setElemText("stat-en-relacion", (stats.relacion.enRelacion || 0) + "%");
    }
  }

  // Setup Event Listeners
  const searchInput = document.getElementById("rector-search-input");
  const recintoSelect = document.getElementById("rector-recinto-select");
  const monthSelect = document.getElementById("rector-month-select");
  const weekSelect = document.getElementById("rector-week-select");

  if (searchInput) searchInput.addEventListener("input", updateRectorDashboard);
  if (recintoSelect) recintoSelect.addEventListener("change", updateRectorDashboard);
  if (monthSelect) monthSelect.addEventListener("change", updateRectorDashboard);
  if (weekSelect) weekSelect.addEventListener("change", updateRectorDashboard);

  // Popover toggle
  const popoverBtn = document.getElementById("btn-toggle-metrics-popover");
  const popoverMenu = document.getElementById("metrics-popover");

  if (popoverBtn && popoverMenu) {
    popoverBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      popoverMenu.classList.toggle("hidden");
    });

    document.addEventListener("click", (e) => {
      if (!popoverMenu.classList.contains("hidden") && !popoverMenu.contains(e.target) && e.target !== popoverBtn) {
        popoverMenu.classList.add("hidden");
      }
    });
  }

  // Checkboxes change listeners
  document.querySelectorAll(".metric-checkbox").forEach(chk => {
    chk.addEventListener("change", () => {
      const metric = chk.getAttribute("data-metric");
      const card = document.querySelector(`.rector-chart-card[data-metric-card="${metric}"]`);
      if (card) {
        if (chk.checked) {
          card.classList.remove("hidden");
        } else {
          card.classList.add("hidden");
        }
      }
      // Re-trigger chart resize for visible ones to align correctly
      setTimeout(() => {
        Object.keys(chartInstances).forEach(key => {
          if (chartInstances[key]) chartInstances[key].resize();
        });
      }, 50);
    });
  });

  // Initial load
  updateRectorDashboard();
}

/* ==========================================================================
   CAROUSEL SECTIONS RENDERING & FADE TRANSITION
   ========================================================================== */
async function renderAllCarousels(filteredData = null) {
  const dataToUse = filteredData || (await getEventsData());
  const statuses = ["activos", "programados", "pasados"];

  statuses.forEach(status => {
    const track = document.getElementById(`track-${status}`);
    const countLabel = document.getElementById(`count-${status}`);
    const dotsContainer = document.getElementById(`dots-${status}`);

    if (!track) return;

    const items = dataToUse.filter(evt => evt.status === status);
    if (countLabel) countLabel.textContent = items.length;

    const numSections = Math.max(1, Math.ceil(items.length / 3));
    if (carouselPages[status] >= numSections) {
      carouselPages[status] = 0;
    }

    renderTrackPageItems(status, items, carouselPages[status]);
    renderCarouselDots(dotsContainer, numSections, status, items);
  });

  if (window.lucide) {
    lucide.createIcons();
  }
}

function renderTrackPageItems(status, items, pageIndex) {
  const track = document.getElementById(`track-${status}`);
  if (!track) return;

  track.innerHTML = "";

  if (items.length === 0) {
    track.innerHTML = `<div class="empty-carousel-msg" style="grid-column: 1 / -1; padding: 20px; color: #9CA3AF; font-style: italic; text-align: center;">No hay actividades en esta categorÃ­a</div>`;
    return;
  }

  const startIndex = pageIndex * 3;
  const pageItems = items.slice(startIndex, startIndex + 3);

  pageItems.forEach(evt => {
    const card = createEventCardElement(evt);
    track.appendChild(card);
  });
}

function renderCarouselDots(dotsContainer, numSections, status, items) {
  if (!dotsContainer) return;
  dotsContainer.innerHTML = "";

  for (let i = 0; i < numSections; i++) {
    const dot = document.createElement("span");
    dot.className = `dot ${i === carouselPages[status] ? "active" : ""}`;
    dot.title = `SecciÃ³n ${i + 1}`;
    dot.onclick = () => goToCarouselSection(status, i, items);
    dotsContainer.appendChild(dot);
  }
}

async function goToCarouselSection(status, targetPage, itemsOverride = null) {
  const rawEvents = itemsOverride ? null : await getEventsData();
  const allEvents = Array.isArray(rawEvents) ? rawEvents : [];
  const items = itemsOverride || allEvents.filter(evt => evt.status === status);
  const numSections = Math.max(1, Math.ceil(items.length / 3));

  if (targetPage < 0 || targetPage >= numSections || targetPage === carouselPages[status]) return;

  const track = document.getElementById(`track-${status}`);
  const dotsContainer = document.getElementById(`dots-${status}`);

  if (track) {
    track.classList.add("fade-out");

    setTimeout(() => {
      carouselPages[status] = targetPage;
      renderTrackPageItems(status, items, targetPage);

      if (dotsContainer) {
        const dots = dotsContainer.querySelectorAll(".dot");
        dots.forEach((d, idx) => {
          if (idx === targetPage) d.classList.add("active");
          else d.classList.remove("active");
        });
      }

      if (window.lucide) {
        lucide.createIcons();
      }

      track.classList.remove("fade-out");
    }, 180);
  }
}

async function changeCarouselPage(status, direction) {
  const rawEvents = await getEventsData();
  const allEvents = Array.isArray(rawEvents) ? rawEvents : [];
  const items = allEvents.filter(evt => evt.status === status);
  const numSections = Math.max(1, Math.ceil(items.length / 3));
  const targetPage = carouselPages[status] + direction;

  if (targetPage >= 0 && targetPage < numSections) {
    goToCarouselSection(status, targetPage, items);
  }
}

function getTagSlug(tag) {
  if (!tag) return "general";
  const lower = String(tag).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const firstWord = lower.trim().split(/\s+/)[0];
  return firstWord.replace(/[^a-z0-9]/g, "") || "general";
}

function createEventCardElement(evt) {
  const card = document.createElement("article");
  card.className = "event-card";
  card.setAttribute("data-id", evt.id);

  const imgSrc = (evt.image && evt.image !== "undefined") ? evt.image : "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=600&q=80";

  card.innerHTML = `
    <div class="card-banner">
      <img src="${imgSrc}" alt="${evt.title}" class="card-banner-img" loading="lazy" />
      <div class="card-banner-overlay">
        <h3 class="card-title">${evt.title}</h3>
        <div class="card-tags">
          ${(evt.tags || []).map(t => `<span class="card-tag tag-${getTagSlug(t)}">${t}</span>`).join("")}
          ${evt.cancelado ? `<span class="card-tag" style="background-color: #ef4444; color: white;">Cancelado</span>` : ''}
        </div>
      </div>
    </div>
    <div class="card-body">
      <div class="info-row">
        <i data-lucide="calendar"></i>
        <span class="info-text">${evt.date}</span>
      </div>
      <div class="info-row">
        <i data-lucide="clock"></i>
        <span class="info-text">${evt.time}</span>
      </div>
      <div class="info-row">
        <i data-lucide="map-pin"></i>
        <span class="info-text">${evt.location}</span>
      </div>

      <div class="card-expanded-details">
        <p class="expanded-desc">${evt.description}</p>
        <div class="expanded-meta">
          <span>👤 ${evt.coordinator}</span>
          <span>👥 ${evt.capacity}</span>
        </div>
        <div class="card-actions">
          ${evt.status === 'programados' ? `
            <button class="btn-card-action btn-action-yellow" onclick="activateActivity('${evt.id}')">Activar Evento</button>
            <button class="btn-card-action btn-action-secondary" onclick="handleEditClick('${evt.id}')">Ver detalles</button>
          ` : evt.status === 'activos' ? `
            <button class="btn-card-action btn-action-secondary" style="background-color: #f97316; color: white;" onclick="finalizeActivity('${evt.id}')">Finalizar evento</button>
            <button class="btn-card-action btn-action-primary" onclick="handleCardClick('${evt.id}')">Ver detalles</button>
          ` : `
            <button class="btn-card-action btn-action-primary" style="width: 100%;" onclick="handleCardClick('${evt.id}')">Ver detalles</button>
          `}
        </div>
      </div>
    </div>
  `;

  return card;
}

/* ==========================================================================
   FORMULARIO DE CREAR ACTIVIDAD (NUEVOS MANEJADORES DE FECHA Y HORA)
   ========================================================================== */
function previewCoverImage(event) {
  const file = event.target.files[0];
  if (!file) return;
  currentUploadedCoverFile = file;

  const reader = new FileReader();
  reader.onload = function (e) {
    currentUploadedCoverUrl = e.target.result;
    const previewImg = document.getElementById("cover-preview-img");
    const iconWrapper = document.getElementById("cover-icon-wrapper");

    if (previewImg && iconWrapper) {
      previewImg.src = currentUploadedCoverUrl;
      previewImg.classList.remove("hidden");
      iconWrapper.style.display = "none";
    }
  };
  reader.readAsDataURL(file);
}

/* Cache local de catálogos e interactividad del formulario de creación */
let globalCatalogosData = null;
let selectedLineamientosMap = new Map(); // id -> justificación

/* --- 1. Info box de Tipo de Actividad (Hover Interaction) --- */
function getCustomTooltipEl() {
  let tooltip = document.getElementById("custom-tipo-floating-tooltip");
  if (!tooltip) {
    tooltip = document.createElement("div");
    tooltip.id = "custom-tipo-floating-tooltip";
    tooltip.className = "custom-floating-tooltip";
    document.body.appendChild(tooltip);
  }
  return tooltip;
}

function showCustomTipoTooltip(event, selectId) {
  const select = document.getElementById(selectId);
  const trigger = event.currentTarget;
  if (!select || !trigger) return;

  const val = select.value;
  let desc = "Seleccione un tipo de actividad para ver su descripción.";

  if (globalCatalogosData && globalCatalogosData.tipos) {
    const tipoObj = globalCatalogosData.tipos.find(t =>
      String(t.id) === String(val) ||
      String(t.nombre).toLowerCase() === String(val).toLowerCase()
    );
    if (tipoObj && tipoObj.descripcion) {
      desc = tipoObj.descripcion;
    }
  }

  const tooltip = getCustomTooltipEl();
  tooltip.textContent = desc;

  const rect = trigger.getBoundingClientRect();
  const tooltipWidth = 230;

  // Posicionar justo AL LADO derecho del ícono (i)
  let left = rect.right + 10;

  // Si no cabe a la derecha de la pantalla, colocarlo a la izquierda del ícono
  if (left + tooltipWidth > window.innerWidth - 10) {
    left = rect.left - tooltipWidth - 10;
  }
  if (left < 10) left = 10;

  // Alineación vertical centrada con el ícono (i)
  let top = rect.top - 6;

  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
  tooltip.classList.add("visible");
}

function hideCustomTipoTooltip() {
  const tooltip = document.getElementById("custom-tipo-floating-tooltip");
  if (tooltip) {
    tooltip.classList.remove("visible");
  }
}

function updateTipoDescripcionUI() { }
function updateDetailTipoDescripcionUI() { }

/* --- 2. Manejo dinámico de fecha de inicio / cierre y aviso de fecha única --- */
function handleDateStartChange() {
  const dateStart = document.getElementById("form-date-start");
  const btnAddEndDate = document.getElementById("btn-add-end-date");
  const endDateContainer = document.getElementById("end-date-container");
  const noticeEl = document.getElementById("date-single-notice");

  if (dateStart && dateStart.value) {
    if (endDateContainer && endDateContainer.classList.contains("hidden")) {
      if (btnAddEndDate) btnAddEndDate.classList.remove("hidden");
      if (noticeEl) noticeEl.classList.remove("hidden");
    }
  } else {
    if (btnAddEndDate) btnAddEndDate.classList.add("hidden");
    if (endDateContainer) endDateContainer.classList.add("hidden");
    if (noticeEl) noticeEl.classList.add("hidden");
  }
}

function handleDateEndChange() {
  const dateEnd = document.getElementById("form-date-end");
  const noticeEl = document.getElementById("date-single-notice");
  if (dateEnd && dateEnd.value) {
    if (noticeEl) noticeEl.classList.add("hidden");
  } else {
    if (noticeEl) noticeEl.classList.remove("hidden");
  }
}

function showEndDateInput() {
  const btnAddEndDate = document.getElementById("btn-add-end-date");
  const endDateContainer = document.getElementById("end-date-container");
  const noticeEl = document.getElementById("date-single-notice");

  if (btnAddEndDate) btnAddEndDate.classList.add("hidden");
  if (endDateContainer) endDateContainer.classList.remove("hidden");
  if (noticeEl) noticeEl.classList.add("hidden");
}

function hideEndDateInput() {
  const dateEnd = document.getElementById("form-date-end");
  const btnAddEndDate = document.getElementById("btn-add-end-date");
  const endDateContainer = document.getElementById("end-date-container");
  const noticeEl = document.getElementById("date-single-notice");

  if (dateEnd) dateEnd.value = "";
  if (endDateContainer) endDateContainer.classList.add("hidden");
  if (btnAddEndDate) btnAddEndDate.classList.remove("hidden");
  if (noticeEl) noticeEl.classList.remove("hidden");
}

/* --- 3. Formateadores de fecha y hora ISO -> Texto legible --- */
function formatDateDisplay(startISO, endISO) {
  if (!startISO) return "Fecha a confirmar";

  const months = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
  ];

  const parseISO = (str) => {
    const parts = str.split("-");
    return { year: parts[0], monthIndex: parseInt(parts[1], 10) - 1, day: parseInt(parts[2], 10) };
  };

  const start = parseISO(startISO);
  if (!endISO || endISO === startISO) {
    return `${start.day} de ${months[start.monthIndex]}, ${start.year}`;
  }

  const end = parseISO(endISO);
  if (start.monthIndex === end.monthIndex) {
    return `${start.day} a ${end.day} de ${months[start.monthIndex]}, ${start.year}`;
  } else {
    return `${start.day} de ${months[start.monthIndex]} a ${end.day} de ${months[end.monthIndex]}, ${start.year}`;
  }
}

function formatTimeDisplay(startISO, endISO) {
  if (!startISO) return "08:00 AM - 04:00 PM";

  const format12H = (str) => {
    const parts = str.split(":");
    let hours = parseInt(parts[0], 10);
    const minutes = parts[1];
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    const formattedHours = hours < 10 ? `0${hours}` : `${hours}`;
    return `${formattedHours}:${minutes} ${ampm}`;
  };

  const startFormatted = format12H(startISO);
  if (!endISO || endISO === startISO) {
    return startFormatted;
  }
  const endFormatted = format12H(endISO);
  return `${startFormatted} - ${endFormatted}`;
}

function renderLineamientosTagSystem(containerId = "lineamientos-tags-container", targetMap = selectedLineamientosMap, onChangeCallback = null) {
  const container = document.getElementById(containerId);
  const countEl = document.getElementById("lineamientos-badge-count");
  if (!container || !globalCatalogosData || !globalCatalogosData.ejes) return;

  if (containerId === "lineamientos-tags-container") {
    // 1. Poblar el select box con los lineamientos no seleccionados
    const select = document.getElementById("form-lineamientos-select");
    if (select) {
      let optionsHtml = '<option value="">Seleccione un eje estratégico...</option>';
      globalCatalogosData.ejes.forEach(eje => {
        optionsHtml += `<optgroup label="${eje.numero_oficial}: ${eje.nombre}">`;
        eje.lineamientos.forEach(lin => {
          const isSelected = targetMap.has(lin.id);
          if (!isSelected) {
            optionsHtml += `<option value="${lin.id}">Lineamiento ${lin.numero_oficial}: ${lin.descripcion}</option>`;
          }
        });
        optionsHtml += '</optgroup>';
      });
      select.innerHTML = optionsHtml;
    }

    // 2. Poblar el contenedor de pills con los seleccionados
    container.innerHTML = "";
    targetMap.forEach((justVal, linId) => {
      let numStr = "Lineamiento";
      let descStr = "";
      for (const eje of globalCatalogosData.ejes) {
        const found = eje.lineamientos.find(l => l.id === linId);
        if (found) {
          numStr = `Lineamiento ${found.numero_oficial}`;
          descStr = found.descripcion;
          break;
        }
      }

      const pill = document.createElement("div");
      pill.className = "eje-pill";
      pill.setAttribute("data-value", linId);
      pill.innerHTML = `
        <span title="${descStr}">${numStr}</span>
        <button type="button" class="btn-remove-pill" onclick="removeLineamientoPill('${linId}', 'lineamientos-tags-container', 'selectedLineamientosMap')">&times;</button>
      `;
      container.appendChild(pill);
    });

    if (countEl) {
      countEl.textContent = `${targetMap.size} / 4 seleccionados`;
    }
  } else {
    // Si estamos en la vista de detalle
    let select = container.querySelector("#detail-lineamientos-select");
    let pillsWrap = container.querySelector("#detail-lineamientos-pills-wrap");

    if (!select) {
      container.innerHTML = `
        <div class="select-wrapper" style="margin-bottom: 12px;">
          <select id="detail-lineamientos-select" class="form-select-pill" style="width: 100%;">
          </select>
          <i data-lucide="chevron-down" class="select-chevron"></i>
        </div>
        <div id="detail-lineamientos-pills-wrap" class="ejes-pills-container" style="margin-top: 12px;">
        </div>
      `;
      select = container.querySelector("#detail-lineamientos-select");
      pillsWrap = container.querySelector("#detail-lineamientos-pills-wrap");

      select.addEventListener("change", () => {
        const val = select.value;
        if (!val) return;
        if (targetMap.size >= 4) {
          showToast("⚠️ Solo se pueden asociar un máximo de 4 lineamientos estratégicos por actividad.");
          select.value = "";
          return;
        }
        targetMap.set(val, "");
        renderLineamientosTagSystem(containerId, targetMap, onChangeCallback);
        renderDetailJustificacionesInputs();
        if (typeof onChangeCallback === "function") onChangeCallback();
      });
    }

    let optionsHtml = '<option value="">Seleccione un eje estratégico...</option>';
    globalCatalogosData.ejes.forEach(eje => {
      optionsHtml += `<optgroup label="${eje.numero_oficial}: ${eje.nombre}">`;
      eje.lineamientos.forEach(lin => {
        const isSelected = targetMap.has(lin.id);
        if (!isSelected) {
          optionsHtml += `<option value="${lin.id}">Lineamiento ${lin.numero_oficial}: ${lin.descripcion}</option>`;
        }
      });
      optionsHtml += '</optgroup>';
    });
    select.innerHTML = optionsHtml;

    pillsWrap.innerHTML = "";
    targetMap.forEach((justVal, linId) => {
      let numStr = "Lineamiento";
      let descStr = "";
      for (const eje of globalCatalogosData.ejes) {
        const found = eje.lineamientos.find(l => l.id === linId);
        if (found) {
          numStr = `Lineamiento ${found.numero_oficial}`;
          descStr = found.descripcion;
          break;
        }
      }

      const pill = document.createElement("div");
      pill.className = "eje-pill";
      pill.setAttribute("data-value", linId);
      pill.innerHTML = `
        <span title="${descStr}">${numStr}</span>
        <button type="button" class="btn-remove-pill" onclick="removeLineamientoPill('${linId}', '${containerId}', 'detailSelectedLineamientosMap')">&times;</button>
      `;
      pillsWrap.appendChild(pill);
    });

    const detailCountBadge = document.querySelector("#detail-lineamientos-card .lineamientos-badge-count");
    if (detailCountBadge) {
      detailCountBadge.textContent = `${targetMap.size} / 4 vinculados`;
    }
  }

  if (window.lucide) lucide.createIcons();
}

function handleAddLineamientoFromSelect() {
  const select = document.getElementById("form-lineamientos-select");
  if (!select) return;

  const val = select.value;
  if (!val) return;

  if (selectedLineamientosMap.size >= 4) {
    showToast("⚠️ Solo se pueden asociar un máximo de 4 lineamientos estratégicos por actividad.");
    select.value = "";
    return;
  }

  selectedLineamientosMap.set(val, "");
  renderLineamientosTagSystem("lineamientos-tags-container", selectedLineamientosMap);
  renderJustificacionesInputs();
  select.value = "";
}

function removeLineamientoPill(id, containerId, mapName) {
  let targetMap = selectedLineamientosMap;
  if (mapName === "detailSelectedLineamientosMap") {
    targetMap = detailSelectedLineamientosMap;
  }

  targetMap.delete(id);

  if (mapName === "selectedLineamientosMap") {
    renderLineamientosTagSystem("lineamientos-tags-container", selectedLineamientosMap);
    renderJustificacionesInputs();
  } else {
    renderLineamientosTagSystem(containerId, detailSelectedLineamientosMap, () => {
      checkIfDetailHasChanges();
    });
    renderDetailJustificacionesInputs();
  }
}


function renderJustificacionesInputs() {
  const container = document.getElementById("lineamientos-justificaciones-container");
  const box = document.getElementById("lineamientos-justificaciones-box");
  if (!container) return;

  container.innerHTML = "";

  if (selectedLineamientosMap.size === 0) {
    if (box) {
      box.style.display = "none";
      box.classList.add("hidden");
    }
    return;
  } else {
    if (box) {
      box.style.display = "block";
      box.classList.remove("hidden");
    }
  }

  let html = `
    <div class="justificaciones-panel">
      <div class="justificaciones-panel-title">
        <span>📋 Ejes / Lineamientos Estratégicos Seleccionados</span>
      </div>
  `;

  selectedLineamientosMap.forEach((justVal, linId) => {
    let numStr = "Lineamiento";
    let descStr = "";
    if (globalCatalogosData && globalCatalogosData.ejes) {
      for (const eje of globalCatalogosData.ejes) {
        const found = eje.lineamientos.find(l => l.id === linId);
        if (found) {
          numStr = `Lineamiento ${found.numero_oficial}`;
          descStr = found.descripcion;
          break;
        }
      }
    }

    html += `
      <div class="justificacion-card" data-card-id="${linId}">
        <div class="justificacion-card-header">
          <span class="justificacion-num-tag">${numStr}</span>
        </div>
        <div class="justificacion-desc-text" style="margin-bottom: 0;">${descStr}</div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
  if (window.lucide) lucide.createIcons();
}

function renderDetailJustificacionesInputs() {
  const container = document.getElementById("detail-lineamientos-justificaciones-container");
  if (!container) return;

  container.innerHTML = "";

  if (detailSelectedLineamientosMap.size === 0) {
    container.style.display = "none";
    container.classList.add("hidden");
    return;
  } else {
    container.style.display = "block";
    container.classList.remove("hidden");
  }

  let html = `
    <div class="justificaciones-panel">
      <div class="justificaciones-panel-title">
        <span>📋 Ejes / Lineamientos Estratégicos Seleccionados</span>
      </div>
  `;

  detailSelectedLineamientosMap.forEach((justVal, linId) => {
    let numStr = "Lineamiento";
    let descStr = "";
    if (globalCatalogosData && globalCatalogosData.ejes) {
      for (const eje of globalCatalogosData.ejes) {
        const found = eje.lineamientos.find(l => l.id === linId);
        if (found) {
          numStr = `Lineamiento ${found.numero_oficial}`;
          descStr = found.descripcion;
          break;
        }
      }
    }

    html += `
      <div class="justificacion-card" data-card-id="${linId}">
        <div class="justificacion-card-header">
          <span class="justificacion-num-tag">${numStr}</span>
        </div>
        <div class="justificacion-desc-text" style="margin-bottom: 0;">${descStr}</div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
  if (window.lucide) lucide.createIcons();
}

function updateDetailJustificacionValue(linId, val, textareaEl) {
  if (detailSelectedLineamientosMap.has(linId)) {
    detailSelectedLineamientosMap.set(linId, val);
    const card = textareaEl ? textareaEl.closest(".justificacion-card") : null;
    if (card) {
      const header = card.querySelector(".justificacion-card-header");
      if (header) {
        const numTag = header.querySelector(".justificacion-num-tag");
        const numText = numTag ? numTag.outerHTML : "";
        if (!val.trim()) {
          header.innerHTML = `${numText}<span class="justificacion-req-tag">* Justificación requerida</span>`;
          textareaEl.style.borderColor = "rgba(239, 68, 68, 0.5)";
        } else {
          header.innerHTML = `${numText}<span class="justificacion-ok-tag">✓ Completado</span>`;
          textareaEl.style.borderColor = "rgba(56, 189, 248, 0.4)";
        }
      }
    }
    checkIfDetailHasChanges();
  }
}

function updateJustificacionValue(linId, val, textareaEl) {
  if (selectedLineamientosMap.has(linId)) {
    selectedLineamientosMap.set(linId, val);
    const card = textareaEl ? textareaEl.closest(".justificacion-card") : null;
    if (card) {
      const header = card.querySelector(".justificacion-card-header");
      if (header) {
        const numTag = header.querySelector(".justificacion-num-tag");
        const numText = numTag ? numTag.outerHTML : "";
        if (!val.trim()) {
          header.innerHTML = `${numText}<span class="justificacion-req-tag">* Justificación requerida</span>`;
          textareaEl.style.borderColor = "rgba(239, 68, 68, 0.5)";
        } else {
          header.innerHTML = `${numText}<span class="justificacion-ok-tag">✓ Completado</span>`;
          textareaEl.style.borderColor = "rgba(56, 189, 248, 0.4)";
        }
      }
    }
  }
}

async function initCrearActividadPage() {
  if (typeof API === "undefined" || !API.getCatalogos) return;
  const catalogos = await API.getCatalogos();
  if (!catalogos) return;

  globalCatalogosData = catalogos;
  selectedLineamientosMap.clear();

  const typeSelect = document.getElementById("form-type");
  if (typeSelect && catalogos.tipos && catalogos.tipos.length > 0) {
    typeSelect.innerHTML = catalogos.tipos.map(t => `<option value="${t.id}">${t.nombre}</option>`).join("");
    updateTipoDescripcionUI();
  }

  const areaSelect = document.getElementById("form-area");
  if (areaSelect && catalogos.unidades && catalogos.unidades.length > 0) {
    areaSelect.innerHTML = catalogos.unidades.map(u => `<option value="${u.id}">${u.nombre} (${u.codigo})</option>`).join("");
  }

  const recintoSelect = document.getElementById("form-recinto");
  const lugarSelect = document.getElementById("form-lugar");

  if (recintoSelect && catalogos.sedes && catalogos.sedes.length > 0) {
    recintoSelect.innerHTML = catalogos.sedes.map(s => `<option value="${s.id}">${s.nombre} (${s.codigo})</option>`).join("");
  }

  function updateLugarOptions() {
    if (!lugarSelect || !catalogos.espacios) return;
    const selectedSedeId = recintoSelect ? recintoSelect.value : null;
    const filtered = selectedSedeId ? catalogos.espacios.filter(e => e.sede_id === selectedSedeId) : catalogos.espacios;
    const list = filtered.length > 0 ? filtered : catalogos.espacios;
    lugarSelect.innerHTML = list.map(e => `<option value="${e.id}">${e.nombre} (Capacidad: ${e.capacidad})</option>`).join("");
  }

  if (recintoSelect) {
    recintoSelect.addEventListener("change", updateLugarOptions);
  }
  updateLugarOptions();

  // Renderizar sistema de etiquetas de lineamientos estratégicos
  renderLineamientosTagSystem();
}

async function saveActivityAndRedirect(e) {
  e.preventDefault();

  const title = document.getElementById("form-title").value.trim();
  const typeSelect = document.getElementById("form-type");
  const areaSelect = document.getElementById("form-area");
  const recintoSelect = document.getElementById("form-recinto");
  const lugarSelect = document.getElementById("form-lugar");
  const desc = document.getElementById("form-desc").value.trim();
  const purpose = document.getElementById("form-purpose") ? document.getElementById("form-purpose").value.trim() : "";

  const dateStart = document.getElementById("form-date-start").value;
  const dateEnd = document.getElementById("form-date-end") && document.getElementById("form-date-end").value ? document.getElementById("form-date-end").value : dateStart;

  const timeStart = document.getElementById("form-time-start").value;
  const timeEnd = document.getElementById("form-time-end").value;

  if (!title) {
    showToast("⚠️ El nombre de la actividad es obligatorio.");
    return;
  }
  if (!dateStart) {
    showToast("⚠️ La fecha de inicio es obligatoria.");
    return;
  }
  if (dateEnd && dateEnd < dateStart) {
    showToast("⚠️ La fecha de cierre no puede ser anterior a la fecha de inicio.");
    return;
  }
  if (!timeStart || !timeEnd) {
    showToast("⚠️ La hora de inicio y de finalización son obligatorias.");
    return;
  }

  let uploadedUrl = null;
  if (currentUploadedCoverFile && typeof API !== "undefined" && API.uploadImage) {
    showToast("📤 Subiendo portada de la actividad...");
    const uploadRes = await API.uploadImage(currentUploadedCoverFile);
    if (uploadRes && uploadRes.success) {
      uploadedUrl = uploadRes.url;
    } else {
      showToast(`⚠️ Error al subir imagen: ${uploadRes ? uploadRes.message : "Error de conexión"}`);
    }
  }

  if (selectedLineamientosMap.size === 0) {
    showToast("⚠️ Debe seleccionar al menos 1 eje estratégico.");
    return;
  }
  if (selectedLineamientosMap.size > 4) {
    showToast("⚠️ Puede seleccionar un máximo de 4 ejes estratégicos.");
    return;
  }
  // Recopilar lineamientos marcados (máximo 4) y auto-generar justificación
  const lineamientosPayload = [];
  selectedLineamientosMap.forEach((justVal, linId) => {
    const autoJustText = desc || purpose || "Actividad vinculada al lineamiento estratégico correspondiente.";
    lineamientosPayload.push({ lineamiento_id: linId, justificacion: autoJustText });
  });
  const payload = {
    title: title,
    description: purpose || desc,
    dateStartISO: dateStart,
    dateEndISO: dateEnd || dateStart,
    timeStartISO: timeStart,
    timeEndISO: timeEnd || timeStart,
    tipo_actividad_id: typeSelect ? typeSelect.value : null,
    unidad_responsable_id: areaSelect ? areaSelect.value : null,
    espacio_fisico_id: lugarSelect && lugarSelect.value ? lugarSelect.value : (recintoSelect ? recintoSelect.value : null),
    lineamientos: lineamientosPayload
  };

  if (uploadedUrl) {
    payload.imagen_url = uploadedUrl;
    payload.image = uploadedUrl;
  }

  let res = null;
  if (typeof API !== "undefined" && API.crearEvento) {
    res = await API.crearEvento(payload);
  }

  if (res && (res.success || res.id)) {
    currentUploadedCoverFile = null;
    currentUploadedCoverUrl = null;
    showToast("✅ Actividad guardada exitosamente en la base de datos");
    setTimeout(() => {
      window.location.href = "index.html";
    }, 900);
  } else {
    showToast(`⚠️ Error al guardar: ${res ? res.message : "Servidor no disponible"}`);
  }
}

function handleAsistenciaClick() {
  if (typeof detailEventId !== "undefined" && detailEventId) {
    window.location.href = `asistencia.html?id=${detailEventId}`;
  } else {
    window.location.href = "asistencia.html";
  }
}

/* DRAWER & UTILS */
function openDrawer() {
  const drawer = document.getElementById("user-drawer");
  const backdrop = document.getElementById("drawer-backdrop");
  if (drawer) drawer.classList.add("active");
  if (backdrop) backdrop.classList.add("active");
}

function closeDrawer() {
  const drawer = document.getElementById("user-drawer");
  const backdrop = document.getElementById("drawer-backdrop");
  if (drawer) drawer.classList.remove("active");
  if (backdrop) backdrop.classList.remove("active");
}

function handleMenuClick(itemLabel) {
  closeDrawer();
  showToast(`ðŸ“Œ Has seleccionado: ${itemLabel}`);
}

async function handleSearchAndFilter() {
  const searchInput = document.getElementById("search-input");
  if (!searchInput) return;

  const searchTerm = searchInput.value.toLowerCase().trim();

  const filterDireccionEl = document.getElementById("filter-direccion");
  const filterDireccion = filterDireccionEl ? filterDireccionEl.value.toLowerCase() : "";

  const filterTipoEl = document.getElementById("filter-tipo");
  const filterTipo = filterTipoEl ? filterTipoEl.value.toLowerCase() : "";

  const filterAreaEl = document.getElementById("filter-area");
  const filterArea = filterAreaEl ? filterAreaEl.value.toLowerCase() : "";

  const filterRecintoEl = document.getElementById("filter-recinto");
  const filterRecinto = filterRecintoEl ? filterRecintoEl.value.toLowerCase() : "";

  const filterFechaEl = document.getElementById("filter-fecha");
  const filterFecha = filterFechaEl ? filterFechaEl.value : "";
  let specificDate = "";
  if (filterFechaEl && filterFechaEl.options[0].text !== "Fecha" && filterFechaEl.options[0].text !== "") {
    specificDate = filterFechaEl.options[0].text.trim(); // format YYYY-MM-DD
  }

  const rawData = await getEventsData();
  const allData = Array.isArray(rawData) ? rawData : [];

  const filtered = allData.filter(evt => {
    // 1. Search term
    const matchesSearch = !searchTerm || (
      (evt.title || "").toLowerCase().includes(searchTerm) ||
      (evt.location || "").toLowerCase().includes(searchTerm) ||
      (evt.description || "").toLowerCase().includes(searchTerm)
    );

    // 2. Dirección Académica
    let matchesDireccion = true;
    if (filterDireccion) {
      const areaVal = (evt.area || "").toLowerCase();
      if (filterDireccion === "ingenieria") matchesDireccion = areaVal === "fi";
      else if (filterDireccion === "arquitectura") matchesDireccion = areaVal === "farq";
      else if (filterDireccion === "ciencias") matchesDireccion = areaVal === "fc";
      else matchesDireccion = areaVal === filterDireccion;
    }

    // 3. Tipo de Evento
    let matchesTipo = true;
    if (filterTipo) {
      const typeVal = (evt.type || "").toLowerCase();
      matchesTipo = typeVal.includes(filterTipo);
    }

    // 4. Área
    let matchesArea = true;
    if (filterArea) {
      const areaVal = (evt.area || "").toLowerCase();
      matchesArea = areaVal === filterArea;
    }

    // 5. Recinto
    let matchesRecinto = true;
    if (filterRecinto) {
      const recintoVal = (evt.recinto || "").toLowerCase();
      if (filterRecinto === "rurp") {
        matchesRecinto = recintoVal === "rusb";
      } else {
        matchesRecinto = recintoVal === filterRecinto;
      }
    }

    // 6. Fecha (fecha_inicio / dateStartISO)
    let matchesFecha = true;
    const evtDate = evt.dateStartISO; // "YYYY-MM-DD"

    if (specificDate) {
      matchesFecha = evtDate === specificDate;
    } else if (filterFecha) {
      const today = new Date();
      // Format today to local YYYY-MM-DD
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      const todayStr = `${year}-${month}-${day}`;

      if (filterFecha === "hoy") {
        matchesFecha = evtDate === todayStr;
      } else if (filterFecha === "semana") {
        const currentDay = today.getDay(); // 0 (Sun) to 6 (Sat)
        const startOfWeek = new Date(today);
        startOfWeek.setDate(today.getDate() - currentDay);
        startOfWeek.setHours(0, 0, 0, 0);

        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(startOfWeek.getDate() + 6);
        endOfWeek.setHours(23, 59, 59, 999);

        // Format start & end
        const sy = startOfWeek.getFullYear();
        const sm = String(startOfWeek.getMonth() + 1).padStart(2, '0');
        const sd = String(startOfWeek.getDate()).padStart(2, '0');
        const startStr = `${sy}-${sm}-${sd}`;

        const ey = endOfWeek.getFullYear();
        const em = String(endOfWeek.getMonth() + 1).padStart(2, '0');
        const ed = String(endOfWeek.getDate()).padStart(2, '0');
        const endStr = `${ey}-${em}-${ed}`;

        matchesFecha = evtDate >= startStr && evtDate <= endStr;
      } else if (filterFecha === "mes") {
        const currentYearMonth = `${year}-${month}`; // "YYYY-MM"
        matchesFecha = (evtDate || "").startsWith(currentYearMonth);
      }
    }

    return matchesSearch && matchesDireccion && matchesTipo && matchesArea && matchesRecinto && matchesFecha;
  });

  await renderAllCarousels(filtered);
}

function handleCardClick(id) {
  window.location.href = `detalle-actividad.html?id=${id}`;
}

function handleEditClick(id) {
  window.location.href = `detalle-actividad.html?id=${id}`;
}

/* ==========================================================================
   PÁGINA DE DETALLE DE EVENTO
   ========================================================================== */

let detailEventId = null;
let detailOriginalData = null;
let detailInEditMode = false;
let detailBaselineData = null;
let detailChartInstances = {};

async function initDetailPage() {
  const params = new URLSearchParams(window.location.search);
  const idParam = params.get("id");
  if (!idParam) { window.location.href = "index.html"; return; }

  // Cargar catálogos dinámicos para emparejar selects con UUIDs reales de la BD
  if (typeof API !== "undefined" && API.getCatalogos) {
    const catalogos = await API.getCatalogos();
    if (catalogos) {
      globalCatalogosData = catalogos;
      const typeSelect = document.getElementById("detail-type");
      if (typeSelect && catalogos.tipos && catalogos.tipos.length > 0) {
        typeSelect.innerHTML = catalogos.tipos.map(t => `<option value="${t.id}">${t.nombre}</option>`).join("");
      }
      const areaSelect = document.getElementById("detail-area");
      if (areaSelect && catalogos.unidades && catalogos.unidades.length > 0) {
        areaSelect.innerHTML = catalogos.unidades.map(u => `<option value="${u.id}">${u.nombre} (${u.codigo})</option>`).join("");
      }
      const recintoSelect = document.getElementById("detail-recinto");
      if (recintoSelect && catalogos.sedes && catalogos.sedes.length > 0) {
        recintoSelect.innerHTML = catalogos.sedes.map(s => `<option value="${s.id}">${s.nombre} (${s.codigo})</option>`).join("");
      }
      const lugarSelect = document.getElementById("detail-lugar");
      if (lugarSelect && catalogos.espacios && catalogos.espacios.length > 0) {
        lugarSelect.innerHTML = catalogos.espacios.map(e => `<option value="${e.id}">${e.nombre} (Capacidad: ${e.capacidad})</option>`).join("");
      }

      if (recintoSelect && lugarSelect) {
        recintoSelect.addEventListener("change", () => {
          const selectedSedeId = recintoSelect.value;
          const filtered = catalogos.espacios.filter(e => e.sede_id === selectedSedeId);
          const list = filtered.length > 0 ? filtered : catalogos.espacios;
          lugarSelect.innerHTML = list.map(e => `<option value="${e.id}">${e.nombre} (Capacidad: ${e.capacidad})</option>`).join("");
        });
      }
    }
  }

  let evt = null;
  if (typeof API !== "undefined" && API.getEventoById) {
    evt = await API.getEventoById(idParam);
  }
  if (!evt) {
    const allData = await getEventsData();
    const id = isNaN(idParam) ? idParam : Number(idParam);
    evt = allData.find(e => e.id === id || e.id == idParam);
  }

  if (!evt) {
    showToast("⚠️ Evento no encontrado.");
    setTimeout(() => { window.location.href = "index.html"; }, 1200);
    return;
  }

  detailEventId = idParam;
  detailOriginalData = JSON.parse(JSON.stringify(evt));
  populateDetailFields(evt);

  // Visibilidad de Secciones de Estadísticas y Asistencia por Status
  const status = evt.status; // 'activos', 'programados', 'pasados'
  const statsCard = document.querySelector(".event-stats-card");
  const asistenciaBtn = document.querySelector(".asistencia-bar-button");
  const btnEditMode = document.getElementById("btn-edit-mode");
  const btnFinalizarTop = document.getElementById("btn-finalize-event"); // El de arriba
  const btnExportData = document.getElementById("btn-export-data");
  const btnVerAsistencias = document.getElementById("btn-ver-asistencias");

  // Reset visibility
  if (btnFinalizarTop) btnFinalizarTop.classList.add("detail-hidden");
  if (btnExportData) btnExportData.classList.remove("detail-hidden"); // Asumir visible por defecto, luego se oculta si no es pasado
  if (btnVerAsistencias) btnVerAsistencias.classList.add("detail-hidden");
  if (btnEditMode) btnEditMode.style.display = "inline-flex";

  if (status === "programados") {
    if (statsCard) statsCard.style.display = "none";
    if (asistenciaBtn) asistenciaBtn.style.display = "none";
    if (btnExportData) btnExportData.classList.add("detail-hidden");
  } else if (status === "pasados") {
    if (statsCard) statsCard.style.display = "block";
    if (asistenciaBtn) asistenciaBtn.style.display = "flex"; // Ahora sí se muestra para eventos pasados
    if (btnEditMode) {
      btnEditMode.classList.add("detail-hidden");
    }
    const btnCancel = document.getElementById("btn-cancel-detail");
    if (btnCancel) {
      btnCancel.classList.add("detail-hidden");
    }
  } else {
    // activos
    if (btnFinalizarTop) btnFinalizarTop.classList.remove("detail-hidden");
    if (btnExportData) btnExportData.classList.add("detail-hidden");
    if (statsCard) statsCard.style.display = "block";
    if (asistenciaBtn) asistenciaBtn.style.display = "flex";
  }

  // Garantizar que los botones de eliminar hora/fecha estén ocultos fuera de edición
  document.getElementById("detail-btn-remove-end-date")?.classList.add("detail-hidden");
  document.getElementById("detail-btn-remove-end-time")?.classList.add("detail-hidden");
  document.getElementById("detail-btn-add-end-date")?.classList.add("detail-hidden");
  document.getElementById("detail-btn-add-end-time")?.classList.add("detail-hidden");
  document.getElementById("btn-undo-detail")?.classList.add("detail-hidden");

  // Inicializar gráficas solo si no es un evento programado
  if (status !== "programados") {
    await initDetailCharts(evt);
  }
}

function getDetailFormValues() {
  return {
    title: document.getElementById("detail-title")?.value || "",
    dateStart: document.getElementById("detail-date-start")?.value || "",
    dateEnd: document.getElementById("detail-date-end")?.value || "",
    endDateHidden: document.getElementById("detail-end-date-container")?.classList.contains("hidden") || false,
    timeStart: document.getElementById("detail-time-start")?.value || "",
    timeEnd: document.getElementById("detail-time-end")?.value || "",
    endTimeHidden: document.getElementById("detail-end-time-container")?.classList.contains("hidden") || false,
    type: document.getElementById("detail-type")?.value || "",
    area: document.getElementById("detail-area")?.value || "",
    recinto: document.getElementById("detail-recinto")?.value || "",
    lugar: document.getElementById("detail-lugar")?.value || "",
    purpose: document.getElementById("form-purpose")?.value || "",
    desc: document.getElementById("detail-desc")?.value || ""
  };
}

function checkIfDetailHasChanges() {
  const btnUndo = document.getElementById("btn-undo-detail");
  if (!detailInEditMode || !detailBaselineData) {
    if (btnUndo) btnUndo.classList.add("detail-hidden");
    return false;
  }

  const current = getDetailFormValues();
  const hasChanges = JSON.stringify(current) !== JSON.stringify(detailBaselineData) || (currentDetailCoverFile !== null);

  if (btnUndo) {
    if (hasChanges) {
      btnUndo.classList.remove("detail-hidden");
    } else {
      btnUndo.classList.add("detail-hidden");
    }
  }
  return hasChanges;
}

function populateDetailFields(evt) {
  // Hero banner
  const heroImg = document.getElementById("detail-hero-img");
  const heroTitle = document.getElementById("detail-hero-title");
  if (heroImg && (evt.image || evt.imagen_url)) heroImg.src = evt.imagen_url || evt.image;
  if (heroTitle) heroTitle.textContent = evt.title || "";

  // Title
  const titleEl = document.getElementById("detail-title");
  if (titleEl) titleEl.value = evt.title || "";

  // Creator
  const creatorEl = document.getElementById("detail-creator");
  if (creatorEl) creatorEl.value = evt.coordinator || evt.creator || "Organizador Universitario";

  // Date
  const dateStartEl = document.getElementById("detail-date-start");
  const dateEndEl = document.getElementById("detail-date-end");
  if (dateStartEl) dateStartEl.value = evt.dateStartISO || "";
  if (dateEndEl && evt.dateEndISO && evt.dateEndISO !== evt.dateStartISO) {
    dateEndEl.value = evt.dateEndISO;
    const endCont = document.getElementById("detail-end-date-container");
    if (endCont) endCont.classList.remove("hidden");
  } else if (dateEndEl) {
    dateEndEl.value = "";
    const endCont = document.getElementById("detail-end-date-container");
    if (endCont) endCont.classList.add("hidden");
  }

  // Time
  const timeStartEl = document.getElementById("detail-time-start");
  const timeEndEl = document.getElementById("detail-time-end");
  if (timeStartEl) timeStartEl.value = evt.timeStartISO || "";
  if (timeEndEl && evt.timeEndISO && evt.timeEndISO !== evt.timeStartISO) {
    timeEndEl.value = evt.timeEndISO;
    const endTimeCont = document.getElementById("detail-end-time-container");
    if (endTimeCont) endTimeCont.classList.remove("hidden");
  } else if (timeEndEl) {
    timeEndEl.value = "";
    const endTimeCont = document.getElementById("detail-end-time-container");
    if (endTimeCont) endTimeCont.classList.add("hidden");
  }

  // Purpose (Propósito / Objetivo)
  const purposeEl = document.getElementById("form-purpose");
  if (purposeEl) purposeEl.value = evt.description || evt.proposito || "";

  // Description
  const descEl = document.getElementById("detail-desc");
  if (descEl) descEl.value = evt.description || "";

  // Select fields (emparejar por UUID si existe, o por texto de fallback)
  if (evt.tipo_actividad_id) setSelectValue("detail-type", evt.tipo_actividad_id);
  else setSelectValue("detail-type", evt.type);

  if (evt.unidad_responsable_id) setSelectValue("detail-area", evt.unidad_responsable_id);
  else setSelectValue("detail-area", evt.area);

  if (evt.sede_id) setSelectValue("detail-recinto", evt.sede_id);
  else setSelectValue("detail-recinto", evt.recinto);

  if (evt.espacio_fisico_id) setSelectValue("detail-lugar", evt.espacio_fisico_id);
  else setSelectValue("detail-lugar", evt.lugar);

  // Lineamientos Estratégicos
  renderDetailLineamientosUI(evt);

  // Actualizar tooltip de tipo de actividad
  updateDetailTipoDescripcionUI();
}

let detailSelectedLineamientosMap = new Map();

function renderDetailLineamientosUI(evt) {
  const readContainer = document.getElementById("detail-lineamientos-readonly-container");
  const countBadge = document.querySelector("#detail-lineamientos-card .lineamientos-badge-count");
  detailSelectedLineamientosMap.clear();

  const lineamientosList = evt && Array.isArray(evt.lineamientos) ? evt.lineamientos : [];

  lineamientosList.forEach(item => {
    const lId = typeof item === "object" ? (item.lineamiento_id || item.id) : item;
    const just = typeof item === "object" ? (item.justificacion || "") : "";
    if (lId) detailSelectedLineamientosMap.set(lId, just);
  });

  if (countBadge) {
    countBadge.textContent = lineamientosList.length > 0
      ? `${lineamientosList.length} / 4 vinculados`
      : "Máx 4 lineamientos";
  }

  // 1. Render modo lectura (vista limpia, concisa y estructurada)
  if (readContainer) {
    if (lineamientosList.length === 0) {
      readContainer.innerHTML = `<p style="color: #94a3b8; font-style: italic; margin: 6px 0;">Sin lineamientos estratégicos asignados a este evento.</p>`;
    } else {
      readContainer.innerHTML = lineamientosList.map(l => {
        let numStr = l.numero_oficial ? `Lineamiento ${l.numero_oficial}` : "Lineamiento";
        let descStr = l.descripcion || l.lineamiento_id || "Lineamiento Estratégico 2026";
        let justStr = l.justificacion ? `<div class="detail-lineamiento-justification">💡 Justificación: ${l.justificacion}</div>` : "";

        // Enriquecer datos usando el catálogo global si fuera necesario
        if ((!l.numero_oficial || !l.descripcion) && globalCatalogosData && globalCatalogosData.ejes) {
          for (const eje of globalCatalogosData.ejes) {
            const found = eje.lineamientos.find(lin => lin.id === (l.lineamiento_id || l.id));
            if (found) {
              numStr = `Lineamiento ${found.numero_oficial}`;
              descStr = found.descripcion;
              break;
            }
          }
        }

        return `
          <div class="detail-lineamiento-item">
            <div class="detail-lineamiento-header">
              <span class="detail-lineamiento-tag-num">${numStr}:</span>
              <span class="detail-lineamiento-desc">${descStr}</span>
            </div>
            ${justStr}
          </div>
        `;
      }).join("");
    }
  }

  // 2. Render editor de lineamientos
  renderDetailLineamientosEditor();

  // 3. Conmutar visibilidad estricta según el estado de edición actual
  const editContainer = document.getElementById("detail-lineamientos-editor-container");
  if (detailInEditMode) {
    if (readContainer) { readContainer.style.display = "none"; readContainer.classList.add("hidden"); }
    if (editContainer) { editContainer.style.display = "block"; editContainer.classList.remove("hidden"); }
  } else {
    if (readContainer) { readContainer.style.display = "block"; readContainer.classList.remove("hidden"); }
    if (editContainer) { editContainer.style.display = "none"; editContainer.classList.add("hidden"); }
  }
}

function renderDetailLineamientosEditor() {
  const tagBox = document.getElementById("detail-lineamientos-tag-system");
  if (!tagBox) return;
  renderLineamientosTagSystem("detail-lineamientos-tag-system", detailSelectedLineamientosMap, () => {
    checkIfDetailHasChanges();
  });
  renderDetailJustificacionesInputs();
}

function setSelectValue(id, value) {
  const el = document.getElementById(id);
  if (!el || !value) return;
  for (let i = 0; i < el.options.length; i++) {
    if (el.options[i].value === value || el.options[i].text === value) {
      el.selectedIndex = i;
      return;
    }
  }
}

/* --- Edit Mode Toggle --- */
function enterEditMode() {
  if (detailOriginalData && detailOriginalData.status === "pasados") {
    showToast("🔒 No se puede editar ni modificar una actividad que ya ha finalizado.");
    return;
  }

  detailInEditMode = true;

  // Toggle readonly en inputs editables
  document.querySelectorAll(".detail-readonly").forEach(el => {
    el.removeAttribute("readonly");
    el.classList.add("detail-editable-active");
  });

  // Habilitar selects
  document.querySelectorAll(".detail-readonly[disabled]").forEach(el => {
    el.removeAttribute("disabled");
  });

  document.querySelectorAll(".form-select-pill.detail-readonly").forEach(el => {
    el.removeAttribute("disabled");
    el.classList.add("detail-editable-active");
  });

  // Mostrar guardar, cambiar portada; ocultar editar
  document.getElementById("btn-edit-mode").classList.add("detail-hidden");
  document.getElementById("btn-save-detail").classList.remove("detail-hidden");
  document.getElementById("btn-change-cover").classList.remove("hidden");

  // Mostrar editor de lineamientos y ocultar vista de solo lectura
  const readLineamientos = document.getElementById("detail-lineamientos-readonly-container");
  const editLineamientos = document.getElementById("detail-lineamientos-editor-container");
  if (readLineamientos) {
    readLineamientos.style.display = "none";
    readLineamientos.classList.add("hidden");
  }
  if (editLineamientos) {
    editLineamientos.style.display = "block";
    editLineamientos.classList.remove("hidden");
  }

  // Refrescar editor y mini-panel de justificaciones
  if (detailOriginalData) {
    renderDetailLineamientosUI(detailOriginalData);
  }

  // Botón Eliminar: solo visible en modo edición para eventos 'programados'
  const btnDelete = document.getElementById("btn-delete-event");
  if (btnDelete) {
    if (detailOriginalData && detailOriginalData.status === "programados") {
      btnDelete.classList.remove("detail-hidden");
    } else {
      btnDelete.classList.add("detail-hidden");
    }
  }

  // Visibilidad de botones de agregar/quitar fecha y hora de cierre
  const ds = document.getElementById("detail-date-start");
  const ts = document.getElementById("detail-time-start");
  const endDateCont = document.getElementById("detail-end-date-container");
  const endTimeCont = document.getElementById("detail-end-time-container");
  const removeDateBtn = document.getElementById("detail-btn-remove-end-date");
  const removeTimeBtn = document.getElementById("detail-btn-remove-end-time");
  const addDateBtn = document.getElementById("detail-btn-add-end-date");
  const addTimeBtn = document.getElementById("detail-btn-add-end-time");

  if (endDateCont && !endDateCont.classList.contains("hidden")) {
    if (removeDateBtn) removeDateBtn.classList.remove("detail-hidden");
    if (addDateBtn) addDateBtn.classList.add("detail-hidden");
  } else if (ds && ds.value) {
    if (addDateBtn) addDateBtn.classList.remove("detail-hidden");
    if (removeDateBtn) removeDateBtn.classList.add("detail-hidden");
  }

  if (endTimeCont && !endTimeCont.classList.contains("hidden")) {
    if (removeTimeBtn) removeTimeBtn.classList.remove("detail-hidden");
    if (addTimeBtn) addTimeBtn.classList.add("detail-hidden");
  } else if (ts && ts.value) {
    if (addTimeBtn) addTimeBtn.classList.remove("detail-hidden");
    if (removeTimeBtn) removeTimeBtn.classList.add("detail-hidden");
  }

  // Guardar estado inicial baseline para detección de cambios
  detailBaselineData = JSON.parse(JSON.stringify(getDetailFormValues()));

  // Vincular eventos input/change a todos los campos para actualizar visibilidad de "Deshacer cambios"
  const formFields = [
    "detail-title", "detail-date-start", "detail-date-end",
    "detail-time-start", "detail-time-end", "detail-type",
    "detail-area", "detail-recinto", "detail-lugar",
    "form-purpose", "detail-desc"
  ];
  formFields.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.removeEventListener("input", checkIfDetailHasChanges);
      el.removeEventListener("change", checkIfDetailHasChanges);
      el.addEventListener("input", checkIfDetailHasChanges);
      el.addEventListener("change", checkIfDetailHasChanges);
    }
  });

  if (ds) ds.addEventListener("change", detailDateStartChanged);
  if (ts) ts.addEventListener("change", detailTimeStartChanged);

  checkIfDetailHasChanges();
}

function detailDateStartChanged() {
  if (!detailInEditMode) return;
  const ds = document.getElementById("detail-date-start");
  const btnAdd = document.getElementById("detail-btn-add-end-date");
  const cont = document.getElementById("detail-end-date-container");
  if (ds.value && cont.classList.contains("hidden")) btnAdd.classList.remove("detail-hidden");
  else if (!ds.value) { btnAdd.classList.add("detail-hidden"); hideDetailEndDate(); }
  checkIfDetailHasChanges();
}

function detailTimeStartChanged() {
  if (!detailInEditMode) return;
  const ts = document.getElementById("detail-time-start");
  const btnAdd = document.getElementById("detail-btn-add-end-time");
  const cont = document.getElementById("detail-end-time-container");
  if (ts.value && cont.classList.contains("hidden")) btnAdd.classList.remove("detail-hidden");
  else if (!ts.value) { btnAdd.classList.add("detail-hidden"); hideDetailEndTime(); }
  checkIfDetailHasChanges();
}

function showDetailEndDate() {
  if (!detailInEditMode) return;
  document.getElementById("detail-btn-add-end-date").classList.add("detail-hidden");
  document.getElementById("detail-end-date-container").classList.remove("hidden");
  document.getElementById("detail-btn-remove-end-date").classList.remove("detail-hidden");
  const endInput = document.getElementById("detail-date-end");
  if (endInput) endInput.removeAttribute("readonly");
  checkIfDetailHasChanges();
}

function hideDetailEndDate() {
  if (!detailInEditMode) return;
  const endInput = document.getElementById("detail-date-end");
  if (endInput) endInput.value = "";
  document.getElementById("detail-end-date-container").classList.add("hidden");
  document.getElementById("detail-btn-remove-end-date").classList.add("detail-hidden");
  if (detailInEditMode) document.getElementById("detail-btn-add-end-date").classList.remove("detail-hidden");
  checkIfDetailHasChanges();
}

function showDetailEndTime() {
  if (!detailInEditMode) return;
  document.getElementById("detail-btn-add-end-time").classList.add("detail-hidden");
  document.getElementById("detail-end-time-container").classList.remove("hidden");
  document.getElementById("detail-btn-remove-end-time").classList.remove("detail-hidden");
  const endInput = document.getElementById("detail-time-end");
  if (endInput) endInput.removeAttribute("readonly");
  checkIfDetailHasChanges();
}

function hideDetailEndTime() {
  if (!detailInEditMode) return;
  const endInput = document.getElementById("detail-time-end");
  if (endInput) endInput.value = "";
  document.getElementById("detail-end-time-container").classList.add("hidden");
  document.getElementById("detail-btn-remove-end-time").classList.add("detail-hidden");
  if (detailInEditMode) document.getElementById("detail-btn-add-end-time").classList.remove("detail-hidden");
  checkIfDetailHasChanges();
}

function undoDetailEdits() {
  if (!detailInEditMode || !detailBaselineData) return;

  currentDetailCoverFile = null;
  if (detailOriginalData) {
    populateDetailFields(detailOriginalData);
  }

  // Restaurar estado de visibilidad de contenedores de fecha/hora de cierre segun el baseline
  const endDateCont = document.getElementById("detail-end-date-container");
  const removeDateBtn = document.getElementById("detail-btn-remove-end-date");
  const addDateBtn = document.getElementById("detail-btn-add-end-date");
  if (detailBaselineData.endDateHidden) {
    if (endDateCont) endDateCont.classList.add("hidden");
    if (removeDateBtn) removeDateBtn.classList.add("detail-hidden");
    if (addDateBtn) addDateBtn.classList.remove("detail-hidden");
  } else {
    if (endDateCont) endDateCont.classList.remove("hidden");
    if (removeDateBtn) removeDateBtn.classList.remove("detail-hidden");
    if (addDateBtn) addDateBtn.classList.add("detail-hidden");
  }

  const endTimeCont = document.getElementById("detail-end-time-container");
  const removeTimeBtn = document.getElementById("detail-btn-remove-end-time");
  const addTimeBtn = document.getElementById("detail-btn-add-end-time");
  if (detailBaselineData.endTimeHidden) {
    if (endTimeCont) endTimeCont.classList.add("hidden");
    if (removeTimeBtn) removeTimeBtn.classList.add("detail-hidden");
    if (addTimeBtn) addTimeBtn.classList.remove("detail-hidden");
  } else {
    if (endTimeCont) endTimeCont.classList.remove("hidden");
    if (removeTimeBtn) removeTimeBtn.classList.remove("detail-hidden");
    if (addTimeBtn) addTimeBtn.classList.add("detail-hidden");
  }

  const btnUndo = document.getElementById("btn-undo-detail");
  if (btnUndo) btnUndo.classList.add("detail-hidden");

  showToast("↩️ Cambios rehechos al estado inicial.");
}

function exitEditMode() {
  detailInEditMode = false;
  detailBaselineData = null;

  document.querySelectorAll(".detail-readonly").forEach(el => {
    el.setAttribute("readonly", "");
    el.classList.remove("detail-editable-active");
  });

  document.querySelectorAll(".form-select-pill.detail-readonly").forEach(el => {
    el.setAttribute("disabled", "");
    el.classList.remove("detail-editable-active");
  });

  document.getElementById("btn-edit-mode").classList.remove("detail-hidden");
  document.getElementById("btn-save-detail").classList.add("detail-hidden");
  document.getElementById("btn-change-cover").classList.add("hidden");
  document.getElementById("btn-undo-detail").classList.add("detail-hidden");

  const btnDelete = document.getElementById("btn-delete-event");
  if (btnDelete) btnDelete.classList.add("detail-hidden");

  const readLineamientos = document.getElementById("detail-lineamientos-readonly-container");
  const editLineamientos = document.getElementById("detail-lineamientos-editor-container");
  if (readLineamientos) {
    readLineamientos.style.display = "block";
    readLineamientos.classList.remove("hidden");
  }
  if (editLineamientos) {
    editLineamientos.style.display = "none";
    editLineamientos.classList.add("hidden");
  }

  // Ocultar botones de agregar y quitar cierre
  document.getElementById("detail-btn-add-end-date")?.classList.add("detail-hidden");
  document.getElementById("detail-btn-add-end-time")?.classList.add("detail-hidden");
  document.getElementById("detail-btn-remove-end-date")?.classList.add("detail-hidden");
  document.getElementById("detail-btn-remove-end-time")?.classList.add("detail-hidden");
}

async function saveDetailChanges() {
  const titleVal = document.getElementById("detail-title").value.trim();
  const dateStartVal = document.getElementById("detail-date-start").value;
  const dateEndVal = document.getElementById("detail-date-end") ? document.getElementById("detail-date-end").value : "";
  const timeStartVal = document.getElementById("detail-time-start").value;
  const timeEndVal = document.getElementById("detail-time-end") ? document.getElementById("detail-time-end").value : "";

  const typeSelect = document.getElementById("detail-type");
  const areaSelect = document.getElementById("detail-area");
  const recintoSelect = document.getElementById("detail-recinto");
  const lugarSelect = document.getElementById("detail-lugar");
  const purposeVal = document.getElementById("form-purpose") ? document.getElementById("form-purpose").value.trim() : "";
  const descVal = document.getElementById("detail-desc") ? document.getElementById("detail-desc").value.trim() : "";

  if (!titleVal) {
    showToast("⚠️ El nombre del evento no puede estar vacío.");
    return;
  }
  if (!dateStartVal) {
    showToast("⚠️ La fecha de inicio es obligatoria.");
    return;
  }
  if (dateEndVal && dateEndVal < dateStartVal) {
    showToast("⚠️ La fecha de cierre no puede ser anterior a la de inicio.");
    return;
  }

  let uploadedUrl = null;
  if (currentDetailCoverFile && typeof API !== "undefined" && API.uploadImage) {
    showToast("📤 Subiendo nueva portada...");
    const uploadRes = await API.uploadImage(currentDetailCoverFile);
    if (uploadRes && uploadRes.success) {
      uploadedUrl = uploadRes.url;
    } else {
      showToast(`⚠️ Error al subir portada: ${uploadRes ? uploadRes.message : ""}`);
    }
  }

  const lineamientosPayload = [];
  detailSelectedLineamientosMap.forEach((just, lId) => {
    const autoJustText = descVal || purposeVal || "Actividad vinculada al lineamiento estratégico correspondiente.";
    lineamientosPayload.push({ lineamiento_id: lId, justificacion: autoJustText });
  });

  const updatedPayload = {
    title: titleVal,
    description: purposeVal || descVal,
    dateStartISO: dateStartVal,
    dateEndISO: dateEndVal || dateStartVal,
    timeStartISO: timeStartVal,
    timeEndISO: timeEndVal || timeStartVal,
    tipo_actividad_id: typeSelect ? typeSelect.value : null,
    unidad_responsable_id: areaSelect ? areaSelect.value : null,
    espacio_fisico_id: lugarSelect && lugarSelect.value ? lugarSelect.value : (recintoSelect ? recintoSelect.value : null),
    lineamientos: lineamientosPayload
  };

  if (uploadedUrl) {
    updatedPayload.imagen_url = uploadedUrl;
    updatedPayload.image = uploadedUrl;
  }

  if (typeof API !== "undefined" && API.updateEvento) {
    const res = await API.updateEvento(detailEventId, updatedPayload);
    if (res && res.success) {
      showToast("✅ Cambios guardados exitosamente en la base de datos");
      const updatedEvt = res.evento || updatedPayload;
      detailOriginalData = updatedEvt;
      currentDetailCoverFile = null;
      exitEditMode();
      populateDetailFields(updatedEvt);
      return;
    } else if (res && res.message) {
      showToast(`⚠️ ${res.message}`);
      return;
    }
  }

  showToast("⚠️ No se pudieron guardar los cambios en el servidor");
  exitEditMode();
  if (detailOriginalData) populateDetailFields(detailOriginalData);
}

function cancelDetailEdits() {
  if (detailInEditMode) {
    // Revertir a datos originales saliendo primero del modo edición
    exitEditMode();
    if (detailOriginalData) populateDetailFields(detailOriginalData);
    showToast("↩️ Cambios descartados");
  } else {
    // Flujo de cancelación del evento (cuando no se está editando)
    if (detailOriginalData && (detailOriginalData.status === 'activos' || detailOriginalData.status === 'programados')) {
      openCancelModal();
    } else {
      window.location.href = "index.html";
    }
  }
}

function openCancelModal() {
  const modal = document.getElementById("modal-cancel-overlay");
  if (modal) modal.classList.remove("detail-hidden");
}

function closeCancelModal() {
  const modal = document.getElementById("modal-cancel-overlay");
  if (modal) modal.classList.add("detail-hidden");
}

async function executeCancelEvent() {
  closeCancelModal();
  let success = false;
  if (typeof API !== "undefined" && API.updateEvento) {
    const res = await API.updateEvento(detailEventId, { status: "pasados", cancelado: true });
    if (res && res.success) {
      success = true;
    }
  }

  // Fallback para entorno mock sin backend activo o error de API
  if (!success) {
    if (detailOriginalData) {
      const updatedEvent = { ...detailOriginalData, status: "pasados", cancelado: true };
      if (typeof ClientCache !== "undefined" && ClientCache.upsertEvento) {
        ClientCache.upsertEvento(updatedEvent);
      }
    }
    if (typeof getEventsData === "function") {
      const allData = await getEventsData();
      const evtId = isNaN(detailEventId) ? detailEventId : Number(detailEventId);
      const evtIndex = allData.findIndex(e => e.id === evtId);
      if (evtIndex !== -1) {
        allData[evtIndex].status = "pasados";
        allData[evtIndex].cancelado = true;
      }
    }
  }

  showToast("🚫 Evento cancelado exitosamente");
  setTimeout(() => { window.location.href = "index.html"; }, 1000);
}

function exitEditMode() {
  detailInEditMode = false;

  document.querySelectorAll(".detail-readonly").forEach(el => {
    el.setAttribute("readonly", "");
    el.classList.remove("detail-editable-active");
  });

  document.querySelectorAll(".form-select-pill.detail-readonly").forEach(el => {
    el.setAttribute("disabled", "");
    el.classList.remove("detail-editable-active");
  });

  document.getElementById("btn-edit-mode").classList.remove("detail-hidden");
  document.getElementById("btn-save-detail").classList.add("detail-hidden");
  document.getElementById("btn-change-cover").classList.add("hidden");

  const btnDelete = document.getElementById("btn-delete-event");
  if (btnDelete) btnDelete.classList.add("detail-hidden");

  // Ocultar botones de agregar cierre
  document.getElementById("detail-btn-add-end-date").classList.add("detail-hidden");
  document.getElementById("detail-btn-add-end-time").classList.add("detail-hidden");
}

function confirmDeleteEvent() {
  const modal = document.getElementById("modal-delete-overlay");
  if (modal) modal.classList.remove("detail-hidden");
}

function closeDeleteModal() {
  const modal = document.getElementById("modal-delete-overlay");
  if (modal) modal.classList.add("detail-hidden");
}

async function executeDeleteEvent() {
  closeDeleteModal();
  if (!detailEventId) return;

  if (typeof API !== "undefined" && API.deleteEvento) {
    const res = await API.deleteEvento(detailEventId);
    if (res && res.success) {
      showToast("✅ Actividad eliminada exitosamente.");
      setTimeout(() => {
        window.location.replace("index.html");
      }, 900);
    } else {
      showToast(`⚠️ ${res ? res.message : "Error al eliminar la actividad."}`);
    }
  }
}

function previewDetailCover(event) {
  const file = event.target.files[0];
  if (!file) return;
  currentDetailCoverFile = file;
  const reader = new FileReader();
  reader.onload = function (e) {
    const heroImg = document.getElementById("detail-hero-img");
    if (heroImg) heroImg.src = e.target.result;
    checkIfDetailHasChanges();
  };
  reader.readAsDataURL(file);
}

/* --- Detail Page Charts --- */
/* --- Detail Page Charts --- */
async function initDetailCharts(evt) {
  if (!evt || !evt.id) return;

  const totalEl = document.getElementById("stat-total-asistentes");
  let apiStats = null;

  if (typeof API !== "undefined" && API.getStatsEvento) {
    apiStats = await API.getStatsEvento(evt.id);
  }

  const totalAsistentes = apiStats ? (apiStats.total_asistentes || 0) : 0;
  if (totalEl) totalEl.textContent = totalAsistentes;

  const CHART_COLORS = {
    blue: "#4A7CF6",
    purple: "#A17CF3",
    orange: "#F8B179",
    yellow: "#FFDD67",
    green: "#34D399",
    red: "#F87171",
    teal: "#2DD4BF",
    indigo: "#818CF8"
  };

  const chartOpts = (extra = {}) => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: "bottom",
        labels: { color: "#e2e8f0", font: { size: 10 }, boxWidth: 12, padding: 8 }
      }
    },
    ...extra
  });

  const rolData = apiStats && apiStats.rol ? apiStats.rol : { estudiantes: 0, trabajadores: 0, otros: 0 };
  const generoData = apiStats && apiStats.genero ? apiStats.genero : { hombres: 0, mujeres: 0 };
  const carrerasList = apiStats && apiStats.carreras ? apiStats.carreras : [];
  const gruposList = apiStats && apiStats.grupos ? apiStats.grupos : [];
  const anosAcademicos = apiStats && apiStats.anos_academicos ? apiStats.anos_academicos : {};

  // 1. Rol Institucional (Donut)
  const ctxRol = document.getElementById("chart-rol-institucional");
  if (ctxRol) {
    if (detailChartInstances.rol) detailChartInstances.rol.destroy();
    detailChartInstances.rol = new Chart(ctxRol, {
      type: "doughnut",
      data: {
        labels: [
          `Estudiantes (${rolData.estudiantes_cnt || 0}) ${rolData.estudiantes}%`,
          `Trabajadores (${rolData.trabajadores_cnt || 0}) ${rolData.trabajadores}%`,
          `General / Otros (${rolData.otros_cnt || 0}) ${rolData.otros}%`
        ],
        datasets: [{
          data: [rolData.estudiantes, rolData.trabajadores, rolData.otros],
          backgroundColor: [CHART_COLORS.blue, CHART_COLORS.purple, CHART_COLORS.orange],
          borderWidth: 0
        }]
      },
      options: { ...chartOpts(), cutout: "55%" }
    });
  }

  // 2. Género (Pie)
  const ctxGenero = document.getElementById("chart-genero");
  if (ctxGenero) {
    if (detailChartInstances.genero) detailChartInstances.genero.destroy();
    detailChartInstances.genero = new Chart(ctxGenero, {
      type: "pie",
      data: {
        labels: [
          `Mujeres (${generoData.mujeres_cnt || 0}) ${generoData.mujeres}%`,
          `Hombres (${generoData.hombres_cnt || 0}) ${generoData.hombres}%`
        ],
        datasets: [{
          data: [generoData.mujeres, generoData.hombres],
          backgroundColor: [CHART_COLORS.purple, CHART_COLORS.blue],
          borderWidth: 0
        }]
      },
      options: chartOpts()
    });
  }

  // 3. Asistencia por Carrera (Bar)
  const ctxCarreras = document.getElementById("chart-carreras");
  if (ctxCarreras) {
    if (detailChartInstances.carreras) detailChartInstances.carreras.destroy();

    const labels = carrerasList.length > 0 ? carrerasList.map(c => c.carrera) : ["Sin asistencias"];
    const values = carrerasList.length > 0 ? carrerasList.map(c => c.count) : [0];

    detailChartInstances.carreras = new Chart(ctxCarreras, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Asistentes",
          data: values,
          backgroundColor: [CHART_COLORS.blue, CHART_COLORS.purple, CHART_COLORS.orange, CHART_COLORS.teal, CHART_COLORS.yellow],
          borderRadius: 6,
          borderWidth: 0
        }]
      },
      options: {
        ...chartOpts({ plugins: { legend: { display: false } } }),
        scales: {
          x: { ticks: { color: "#e2e8f0", font: { size: 9 } }, grid: { color: "rgba(255,255,255,0.07)" } },
          y: { ticks: { color: "#e2e8f0", font: { size: 9 } }, grid: { color: "rgba(255,255,255,0.07)" }, beginAtZero: true }
        }
      }
    });
  }

  // 4. Asistencia por Grupos (Bar)
  const ctxGrupos = document.getElementById("chart-grupos");
  if (ctxGrupos) {
    if (detailChartInstances.grupos) detailChartInstances.grupos.destroy();

    const labels = gruposList.length > 0 ? gruposList.map(g => g.grupo) : ["Sin asistencias"];
    const values = gruposList.length > 0 ? gruposList.map(g => g.count) : [0];

    detailChartInstances.grupos = new Chart(ctxGrupos, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Integrantes",
          data: values,
          backgroundColor: CHART_COLORS.teal,
          borderRadius: 5,
          borderWidth: 0
        }]
      },
      options: {
        ...chartOpts({ plugins: { legend: { display: false } } }),
        scales: {
          x: { ticks: { color: "#e2e8f0", font: { size: 9 } }, grid: { display: false } },
          y: { ticks: { color: "#e2e8f0", font: { size: 9 } }, grid: { color: "rgba(255,255,255,0.07)" }, beginAtZero: true }
        }
      }
    });
  }

  // 5. Año Académico (Bar)
  const ctxAnos = document.getElementById("chart-anos-academicos");
  if (ctxAnos) {
    if (detailChartInstances.anos) detailChartInstances.anos.destroy();

    const keys = Object.keys(anosAcademicos);
    const labels = keys.length > 0 ? keys : ["1º Año", "2º Año", "3º Año", "4º Año", "5º Año"];
    const values = keys.length > 0 ? keys.map(k => anosAcademicos[k]) : [0, 0, 0, 0, 0];

    detailChartInstances.anos = new Chart(ctxAnos, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Estudiantes",
          data: values,
          backgroundColor: CHART_COLORS.indigo,
          borderRadius: 5,
          borderWidth: 0
        }]
      },
      options: {
        ...chartOpts({ plugins: { legend: { display: false } } }),
        scales: {
          x: { ticks: { color: "#e2e8f0", font: { size: 9 } }, grid: { display: false } },
          y: { ticks: { color: "#e2e8f0", font: { size: 9 } }, grid: { color: "rgba(255,255,255,0.07)" }, beginAtZero: true }
        }
      }
    });
  }

  // 6. Procedencia Geográfica (Bar)
  const ctxGeo = document.getElementById("chart-geografia-evento");
  if (ctxGeo) {
    if (detailChartInstances.geografia) detailChartInstances.geografia.destroy();

    const geoData = apiStats && apiStats.geografia ? apiStats.geografia : {};
    const geoKeys = Object.keys(geoData);
    const labels = geoKeys.length > 0 ? geoKeys : ["Managua"];
    const values = geoKeys.length > 0 ? geoKeys.map(k => geoData[k]) : [0];

    detailChartInstances.geografia = new Chart(ctxGeo, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Asistentes por Depto",
          data: values,
          backgroundColor: CHART_COLORS.orange,
          borderRadius: 5,
          borderWidth: 0
        }]
      },
      options: {
        ...chartOpts({ plugins: { legend: { display: false } } }),
        scales: {
          x: { ticks: { color: "#e2e8f0", font: { size: 9 } }, grid: { display: false } },
          y: { ticks: { color: "#e2e8f0", font: { size: 9 } }, grid: { color: "rgba(255,255,255,0.07)" }, beginAtZero: true }
        }
      }
    });
  }
}

function generateMockStats(seed) {
  // Deterministic pseudo-random based on seed so each event has consistent demo data
  const r = (min, max) => {
    seed = (seed * 1664525 + 1013904223) & 0xffffffff;
    return min + Math.abs(seed % (max - min + 1));
  };
  const e = r(40, 70), d = r(15, 30), a = r(5, 15);
  const v = 100 - e - d - a;
  const hombres = r(40, 65), mujeres = 100 - hombres;
  const f1 = r(20, 60), f2 = r(15, 50), f3 = r(10, 40), f4 = r(8, 35), f5 = r(5, 25);
  const nat = r(78, 95), ext = 100 - nat;
  const lab = r(25, 45), solo = 100 - lab;
  const sol = r(55, 75), rel = 100 - sol;
  const mes = r(65, 82), mis = r(8, 18), cri = r(3, 8), otras = 100 - mes - mis - cri;
  const urb = r(60, 80), rur = 100 - urb;
  const natCap = r(78, 90), dis = r(6, 15), def = 100 - natCap - dis;

  // New formacion & areaConocimiento metrics
  const f_est = r(50, 65), f_ing = r(15, 30), f_doc = r(5, 15), f_lic = 100 - f_est - f_ing - f_doc;
  const a_edu = r(50, 65), a_art = r(15, 30), a_tec = r(8, 18), a_inf = 100 - a_edu - a_art - a_tec;

  return {
    rol: { estudiantes: e, docentes: d, admin: a, visitantes: Math.max(v, 0) },
    genero: { hombres, mujeres },
    facultades: [f1, f2, f3, f4, f5],
    edades: [r(5, 20), r(30, 80), r(20, 70), r(10, 45), r(5, 30), r(2, 15)],
    capacidades: { naturales: natCap, discapacidad: dis, deficiencias: Math.max(def, 0) },
    nacionalidad: { nacionales: nat, extranjeros: ext },
    laboral: { soloEstudian: solo, trabajan: lab },
    relacion: { solteros: sol, enRelacion: rel },
    etnias: { mestizos: mes, miskitos: mis, criollos: cri, otras: Math.max(otras, 0) },
    procedencia: { urbano: urb, rural: rur },
    formacion: { bachillerato: f_est, ingenieria: f_ing, doctorado: f_doc, licenciatura: Math.max(f_lic, 0) },
    areaConocimiento: { educacion: a_edu, artes: a_art, tecnologia: a_tec, informacion: Math.max(a_inf, 0) }
  };
}

function showToast(message) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(20px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ==========================================================================
   LÃ“GICA DE ASISTENCIA Y CONTROLES
   ========================================================================== */
/* ==========================================================================
   LÓGICA DE ASISTENCIA Y CONTROLES PULIDOS
   ========================================================================== */
let currentAsistenciaEventId = null;
let isAsistenciaAbierta = true;

async function setupAsistenciaView() {
  if (document.body.getAttribute("data-page") !== "asistencia") return;

  const darkTitle = document.getElementById("asistencia-dark-title");
  const heroTitle = document.querySelector(".asistencia-hero-title");
  const badgeStatus = document.getElementById("badge-asistencia-status");
  const btnToggleAsistencia = document.getElementById("btn-toggle-asistencia");
  const txtToggleAsistencia = document.getElementById("txt-toggle-asistencia");

  const escanerInput = document.getElementById("escaner-input");
  const btnEscanerSubmit = document.getElementById("btn-escaner-submit");
  const escanerFeedback = document.getElementById("escaner-feedback");

  const btnModoManual = document.getElementById("btn-modo-manual");
  const formManual = document.getElementById("form-manual-container");
  const btnCerrarManual = document.getElementById("btn-cerrar-manual");
  const btnEjecutarBusqueda = document.getElementById("btn-ejecutar-busqueda-manual");
  const resultsContainer = document.getElementById("manual-search-results");

  const btnAbrirNuevo = document.getElementById("btn-abrir-estudiante-nuevo");
  const formNuevo = document.getElementById("form-estudiante-nuevo-container");
  const btnCerrarNuevo = document.getElementById("btn-cerrar-nuevo-estudiante");
  const btnGuardarNuevo = document.getElementById("btn-guardar-estudiante-nuevo");

  // 1. Identificar evento activo
  const urlParams = new URLSearchParams(window.location.search);
  let eventId = urlParams.get("id");

  if (!eventId && typeof API !== "undefined" && API.getEventos) {
    const activeEvents = await API.getEventos({ status: "activos" });
    if (activeEvents && activeEvents.length > 0) {
      eventId = activeEvents[0].id;
    } else {
      const allEvents = await API.getEventos();
      if (allEvents && allEvents.length > 0) eventId = allEvents[0].id;
    }
  }

  currentAsistenciaEventId = eventId;

  // 2. Función para actualizar UI según si las asistencias están abiertas/cerradas
  function setAsistenciaAbiertaUI(abierta) {
    isAsistenciaAbierta = abierta;
    if (badgeStatus) {
      if (abierta) {
        badgeStatus.className = "badge-status badge-abierta";
        badgeStatus.textContent = "● Asistencia Abierta";
      } else {
        badgeStatus.className = "badge-status badge-cerrada";
        badgeStatus.textContent = "● Asistencia Cerrada";
      }
    }

    if (btnToggleAsistencia && txtToggleAsistencia) {
      if (abierta) {
        btnToggleAsistencia.className = "btn-asistencia-switch btn-cerrar-asistencia";
        txtToggleAsistencia.textContent = "Cerrar asistencias";
      } else {
        btnToggleAsistencia.className = "btn-asistencia-switch btn-abrir-asistencia";
        txtToggleAsistencia.textContent = "Abrir asistencias";
      }
    }

    if (escanerInput) {
      escanerInput.disabled = !abierta;
      if (!abierta) {
        if (escanerFeedback) escanerFeedback.innerHTML = "<span style='color: #f87171;'>🔒 La toma de asistencias está cerrada para esta actividad.</span>";
      } else {
        if (escanerFeedback) escanerFeedback.innerHTML = "💡 Listo para recibir lecturas del escáner (Plug and Play).";
      }
    }

    // Bloquear / Desbloquear botón Estudiante Nuevo y cerrar/ocultar el panel si la asistencia se cierra
    if (btnAbrirNuevo) {
      btnAbrirNuevo.disabled = !abierta;
      btnAbrirNuevo.style.opacity = abierta ? "1" : "0.5";
      btnAbrirNuevo.style.cursor = abierta ? "pointer" : "not-allowed";
    }

    if (formNuevo) {
      if (!abierta) {
        formNuevo.classList.remove("open");
        formNuevo.style.display = "none";
      } else {
        formNuevo.style.display = "";
      }
    }

    if (!abierta) {
      selectedAsistenciaIds.clear();
      updateAsistenciaSeleccionUI();
    }
  }

  let currentAsistentesList = [];

  // 3. Cargar datos del evento y tabla de asistencias (con fallback automático si la ID es inválida o fue reiniciada)
  async function loadEventAndAttendance() {
    if (typeof API === "undefined" || !API.getAsistentesEvento) return;

    if (currentAsistenciaEventId) {
      const data = await API.getAsistentesEvento(currentAsistenciaEventId);

      if (data && data.success) {
        if (data.evento && data.evento.nombre) {
          if (darkTitle) darkTitle.textContent = data.evento.nombre.toUpperCase();
          if (heroTitle) heroTitle.innerHTML = data.evento.nombre.replace(" ", "<br>");
        }

        // Verificar si el evento ya está finalizado ("pasados")
        let isPasado = data.evento && data.evento.status === "pasados";
        if (typeof getEventsData === "function") {
          const allEvts = await getEventsData();
          const foundEvt = allEvts.find(e => e.id == currentAsistenciaEventId);
          if (foundEvt && foundEvt.status === "pasados") {
            isPasado = true;
          }
        }

        if (isPasado) {
          setAsistenciaAbiertaUI(false);
          // Ocultar controles de edición completamente (botón toggle, escáner, añadir alumno)
          if (btnToggleAsistencia) btnToggleAsistencia.style.display = "none";
          const escanerBar = document.getElementById("escaner-bar-container");
          if (escanerBar) escanerBar.style.display = "none";
          if (badgeStatus) {
            badgeStatus.className = "badge-status badge-cerrada";
            badgeStatus.textContent = "● Evento Finalizado (Solo Lectura)";
          }
        } else {
          setAsistenciaAbiertaUI(data.asistencia_abierta !== false);
          if (btnToggleAsistencia) btnToggleAsistencia.style.display = "";
          const escanerBar = document.getElementById("escaner-bar-container");
          if (escanerBar) escanerBar.style.display = "";
        }

        currentAsistentesList = data.asistentes || [];
        renderTablaAsistencia(currentAsistentesList);
        return;
      }
    }

    // Fallback: Si el ID del evento en la URL no existe (ej. tras re-sembrar la BD), seleccionar automáticamente el primer evento activo
    if (API.getEventos) {
      const activeEvents = await API.getEventos({ status: "activos" });
      let validEvent = (activeEvents && activeEvents.length > 0) ? activeEvents[0] : null;

      if (!validEvent) {
        const allEvents = await API.getEventos();
        if (allEvents && allEvents.length > 0) validEvent = allEvents[0];
      }

      if (validEvent) {
        currentAsistenciaEventId = validEvent.id;
        window.history.replaceState({}, "", `asistencia.html?id=${validEvent.id}`);
        showToast(`ℹ️ Cargada la actividad activa: ${validEvent.nombre}`);

        const retryData = await API.getAsistentesEvento(currentAsistenciaEventId);
        if (retryData && retryData.success) {
          if (darkTitle) darkTitle.textContent = (retryData.evento?.nombre || validEvent.nombre).toUpperCase();
          if (heroTitle) heroTitle.innerHTML = (retryData.evento?.nombre || validEvent.nombre).replace(" ", "<br>");
          
          if (validEvent.status === "pasados") {
            setAsistenciaAbiertaUI(false);
            if (btnToggleAsistencia) btnToggleAsistencia.style.display = "none";
            const escanerBar = document.getElementById("escaner-bar-container");
            if (escanerBar) escanerBar.style.display = "none";
            if (badgeStatus) {
              badgeStatus.className = "badge-status badge-cerrada";
              badgeStatus.textContent = "● Evento Finalizado (Solo Lectura)";
            }
          } else {
            setAsistenciaAbiertaUI(retryData.asistencia_abierta !== false);
            if (btnToggleAsistencia) btnToggleAsistencia.style.display = "";
            const escanerBar = document.getElementById("escaner-bar-container");
            if (escanerBar) escanerBar.style.display = "";
          }

          currentAsistentesList = retryData.asistentes || [];
          renderTablaAsistencia(currentAsistentesList);
        }
      } else {
        if (darkTitle) darkTitle.textContent = "NO HAY ACTIVIDADES ACTIVAS";
        showToast("⚠️ No se encontraron actividades disponibles para asistencia.");
      }
    }
  }

  // 4. Lógica de Selección Múltiple y Eliminación de Asistencia (Ctrl+Click / Shift+Click)
  let selectedAsistenciaIds = new Set();
  let lastSelectedIndex = null;
  const btnEliminarSeleccion = document.getElementById("btn-eliminar-asistencia-seleccion");
  const countSeleccionEl = document.getElementById("count-asistencia-seleccion");

  function updateAsistenciaSeleccionUI() {
    const tbody = document.querySelector(".asistencia-table tbody");
    if (!tbody) return;

    const rows = tbody.querySelectorAll("tr[data-asist-id]");
    rows.forEach(tr => {
      const id = tr.getAttribute("data-asist-id");
      if (id && selectedAsistenciaIds.has(id)) {
        tr.classList.add("selected-row");
      } else {
        tr.classList.remove("selected-row");
      }
    });

    const count = selectedAsistenciaIds.size;
    if (countSeleccionEl) countSeleccionEl.textContent = count;

    if (btnEliminarSeleccion) {
      if (count > 0) {
        btnEliminarSeleccion.style.display = "inline-flex";
      } else {
        btnEliminarSeleccion.style.display = "none";
      }
    }
  }

  function clearAsistenciaSeleccion() {
    selectedAsistenciaIds.clear();
    lastSelectedIndex = null;
    updateAsistenciaSeleccionUI();
  }

  // Listener global para deseleccionar al hacer clic fuera de las filas o fuera de la tabla
  document.addEventListener("click", (e) => {
    const isRowClick = e.target.closest(".asistencia-table tbody tr[data-asist-id]");
    const isDeleteBtnClick = e.target.closest("#btn-eliminar-asistencia-seleccion");

    if (!isRowClick && !isDeleteBtnClick) {
      clearAsistenciaSeleccion();
    }
  });

  // Listener para el botón único de eliminación de selección
  if (btnEliminarSeleccion) {
    btnEliminarSeleccion.addEventListener("click", async (e) => {
      e.stopPropagation();
      const count = selectedAsistenciaIds.size;
      if (count === 0) return;

      let confirmMsg = "";
      if (count === 1) {
        const selectedId = Array.from(selectedAsistenciaIds)[0];
        const row = document.querySelector(`tr[data-asist-id="${selectedId}"]`);
        const nombre = row ? (row.getAttribute("data-nombre") || "el estudiante") : "el estudiante";
        confirmMsg = `⚠️ ¿Estás seguro de que deseas eliminar la asistencia de "${nombre}"?\n\nEsta acción corregirá el recuento de asistentes y no se puede deshacer.`;
      } else {
        confirmMsg = `⚠️ ¿Estás seguro de que deseas eliminar las ${count} asistencias seleccionadas?\n\nEsta acción corregirá el recuento de asistentes y no se puede deshacer.`;
      }

      if (!confirm(confirmMsg)) return;

      const idsToDelete = Array.from(selectedAsistenciaIds);
      let successCount = 0;

      for (const id of idsToDelete) {
        const res = await API.eliminarAsistencia(id);
        if (res && res.success) successCount++;
      }

      showToast(count === 1 ? `✅ Asistencia eliminada correctamente.` : `✅ ${successCount} de ${count} asistencias eliminadas correctamente.`);
      clearAsistenciaSeleccion();
      await loadEventAndAttendance();
    });
  }

  // 5. Renderizar Tabla de Asistentes con Selección Interactiva
  function renderTablaAsistencia(asistentes) {
    const tbody = document.querySelector(".asistencia-table tbody");
    const countEl = document.querySelector(".asistentes-count");

    if (countEl) {
      const numStr = (asistentes.length < 10 ? "0" : "") + asistentes.length;
      countEl.textContent = `Asistentes: ${numStr}`;
    }

    if (!tbody) return;
    tbody.innerHTML = "";
    selectedAsistenciaIds.clear();
    lastSelectedIndex = null;
    updateAsistenciaSeleccionUI();

    if (asistentes.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="26" style="text-align: center; color: #6b7280; padding: 25px;">
            No hay asistencias registradas aún para esta actividad.
          </td>
        </tr>
      `;
      return;
    }

    asistentes.forEach((a, idx) => {
      const tr = document.createElement("tr");
      tr.setAttribute("data-asist-id", a.id);
      tr.setAttribute("data-nombre", a.nombres_apellidos);

      if (selectedAsistenciaIds.has(a.id)) {
        tr.classList.add("selected-row");
      }

      tr.innerHTML = `
        <td>${a.numero_unico || 'N/A'}</td>
        <td><strong>${a.nombres_apellidos || a.nombre || 'N/A'}</strong></td>
        <td>${a.sexo || 'Masculino'}</td>
        <td>${a.edad || 21}</td>
        <td>${a.nacionalidad || 'Nicaragüense'}</td>
        <td>${a.pais_procedencia || 'Nicaragua'}</td>
        <td>${a.etnia || 'Mestizo'}</td>
        <td>${a.departamento_procedencia || 'Managua'}</td>
        <td>${a.municipio_procedencia || 'Managua'}</td>
        <td>${a.departamento_residencia || 'Managua'}</td>
        <td>${a.municipio_residencia || 'Managua'}</td>
        <td>${a.tipo_ingreso || 'Regular'}</td>
        <td>${a.sede || 'RUSB'}</td>
        <td>${a.departamento_sede || 'Managua'}</td>
        <td>${a.municipio_sede || 'Managua'}</td>
        <td>${a.programa_especial || 'Ninguno'}</td>
        <td>${a.departamento_unicam || 'N/A'}</td>
        <td>${a.municipio_unicam || 'N/A'}</td>
        <td>${a.nivel_formacion || 'Grado'}</td>
        <td>${a.carrera || 'General'}</td>
        <td>${a.area || 'DACTIC'}</td>
        <td>${a.duracion_carrera || '5 Años'}</td>
        <td>${a.ano_academico || '1º Año'}</td>
        <td>${a.regimen || 'Semestral'}</td>
        <td>${a.modalidad || 'Presencial'}</td>
        <td>${a.turno || 'Diurno'}</td>
      `;

      // Event listener para selección de fila (Click normal, Ctrl+Click y Shift+Click)
      tr.addEventListener("click", (e) => {
        if (!isAsistenciaAbierta) return; // Si la asistencia está cerrada, no es seleccionable ninguna fila
        e.stopPropagation(); // Evitar que el listener global deseleccione
        const rows = Array.from(tbody.querySelectorAll("tr[data-asist-id]"));
        const currentIndex = idx;

        if (e.ctrlKey || e.metaKey) {
          // Ctrl + Click: Alternar selección de esta fila
          if (selectedAsistenciaIds.has(a.id)) {
            selectedAsistenciaIds.delete(a.id);
          } else {
            selectedAsistenciaIds.add(a.id);
          }
          lastSelectedIndex = currentIndex;
        } else if (e.shiftKey) {
          // Shift + Click: Selección por rango desde lastSelectedIndex hasta currentIndex
          if (lastSelectedIndex !== null) {
            const start = Math.min(lastSelectedIndex, currentIndex);
            const end = Math.max(lastSelectedIndex, currentIndex);
            if (!e.ctrlKey) selectedAsistenciaIds.clear();
            for (let i = start; i <= end; i++) {
              const rowId = rows[i]?.getAttribute("data-asist-id");
              if (rowId) selectedAsistenciaIds.add(rowId);
            }
          } else {
            selectedAsistenciaIds.clear();
            selectedAsistenciaIds.add(a.id);
            lastSelectedIndex = currentIndex;
          }
        } else {
          // Clic Normal: Seleccionar únicamente esta fila
          selectedAsistenciaIds.clear();
          selectedAsistenciaIds.add(a.id);
          lastSelectedIndex = currentIndex;
        }

        updateAsistenciaSeleccionUI();
      });

      tbody.appendChild(tr);
    });

    if (window.lucide) lucide.createIcons();
  }

  // 5. Helper robusto para registrar asistencia con auto-recuperación si la ID del evento caducó
  async function ejecutarRegistroAsistencia(identifier) {
    if (!currentAsistenciaEventId) {
      await loadEventAndAttendance();
    }

    if (!currentAsistenciaEventId) {
      return { success: false, message: "No hay ninguna actividad activa seleccionada" };
    }

    let res = await API.registrarAsistencia(currentAsistenciaEventId, identifier);

    // Si la ID del evento era obsoleta (404 / 'El evento no existe'), recuperar evento activo real y reintentar
    if (res && !res.success && res.message && (res.message.includes("evento no existe") || res.message.includes("El evento no existe"))) {
      console.warn("Evento caducado detectado. Obteniendo actividad activa actualizada...");
      await loadEventAndAttendance();
      if (currentAsistenciaEventId) {
        res = await API.registrarAsistencia(currentAsistenciaEventId, identifier);
      }
    }

    return res;
  }

  // 6. Botón Conmutar Cerrar / Abrir Asistencia
  if (btnToggleAsistencia) {
    btnToggleAsistencia.addEventListener("click", async () => {
      if (!currentAsistenciaEventId) {
        await loadEventAndAttendance();
      }

      if (!currentAsistenciaEventId) {
        showToast("⚠️ No hay evento activo seleccionado.");
        return;
      }

      let res = await API.toggleEstadoAsistencia(currentAsistenciaEventId);
      if (res && !res.success && res.message && res.message.includes("evento no existe")) {
        await loadEventAndAttendance();
        if (currentAsistenciaEventId) {
          res = await API.toggleEstadoAsistencia(currentAsistenciaEventId);
        }
      }

      if (res && res.success) {
        setAsistenciaAbiertaUI(res.asistencia_abierta);
        showToast(`✅ ${res.message}`);
        await loadEventAndAttendance(); // Re-cargar la tabla para garantizar que todos los asistentes se mantengan visibles
      } else {
        showToast(`⚠️ ${res ? res.message : "Error al cambiar estado"}`);
      }
    });
  }

  // 7. Lectura del Escáner 3nStar Sc050 (Entrada inmediata por Cédula/CUP/Carné al presionar Enter)
  async function procesarEscaneo() {
    if (!isAsistenciaAbierta) {
      showToast("🔒 La toma de asistencias está cerrada para este evento.");
      return;
    }

    if (!escanerInput) return;
    const identifier = escanerInput.value.trim();
    if (!identifier) return;

    if (escanerFeedback) escanerFeedback.innerHTML = "⏳ Verificando en la base de datos...";

    const res = await ejecutarRegistroAsistencia(identifier);

    if (res && res.success) {
      const nombre = res.asistente ? res.asistente.nombre : "Asistente";
      showToast(`✅ Asistencia registrada: ${nombre}`);
      if (escanerFeedback) escanerFeedback.innerHTML = `<span style="color: #4ade80;">✅ Asistencia marcada: <strong>${nombre}</strong> (${identifier})</span>`;
      escanerInput.value = "";
      if (resultsContainer) resultsContainer.style.display = "none";
      await loadEventAndAttendance();
    } else if (res && res.not_found) {
      showToast("⚠️ No se encontró al estudiante en la base de datos.");
      if (escanerFeedback) escanerFeedback.innerHTML = `<span style="color: #f87171;">⚠️ No se encontró al estudiante con cédula/código '${identifier}' en la BD.</span>`;
    } else {
      showToast(`⚠️ ${res ? res.message : "Error al marcar asistencia"}`);
      if (escanerFeedback) escanerFeedback.innerHTML = `<span style="color: #f87171;">⚠️ ${res ? res.message : "Error"}</span>`;
    }
  }

  // 8. Buscador Automático con Filtros Integrados (Carrera, Grupo y Nombre/Cédula)
  async function procesarBusquedaFiltrada() {
    if (!resultsContainer) return;
    const q = escanerInput ? escanerInput.value.trim() : "";
    const carrera = document.getElementById("filter-carrera-select")?.value || "";
    const grupo = document.getElementById("filter-grupo-select")?.value || "";

    if (!q && !carrera && !grupo) {
      resultsContainer.style.display = "none";
      return;
    }

    resultsContainer.style.display = "grid";
    resultsContainer.innerHTML = "<div style='color: #94a3b8; grid-column: 1/-1; text-align: center; padding: 12px;'>🔍 Buscando en padrón...</div>";

    const res = await API.buscarEstudiantes({ query: q, carrera, grupo });

    if (res && res.success && res.estudiantes.length > 0) {
      resultsContainer.innerHTML = "";
      res.estudiantes.forEach(est => {
        const card = document.createElement("div");
        card.className = "student-result-card";
        const ident = est.cedula || est.numero_unico || est.carnet;

        // Verificar si el estudiante YA está registrado en las asistencias del evento actual
        const yaAsistio = currentAsistentesList.find(a =>
          (a.cedula && est.cedula && a.cedula === est.cedula) ||
          (a.numero_unico && est.numero_unico && a.numero_unico === est.numero_unico) ||
          (a.carnet && est.carnet && a.carnet === est.carnet)
        );

        if (yaAsistio) {
          card.innerHTML = `
            <div class="student-card-info">
              <h4>${est.nombres_apellidos} <span class="badge-ya-asistio">✓ Registrado</span></h4>
              <p><strong>Cédula / CUP:</strong> ${est.cedula} | ${est.numero_unico}</p>
              <p><strong>Carrera:</strong> ${est.carrera} (${est.grupo})</p>
              <p><strong>Sede:</strong> ${est.sede}</p>
            </div>
            <button class="btn-ubicar-en-tabla-card" data-asist-id="${yaAsistio.id}" data-nombre="${est.nombres_apellidos}">
              Ubicar en Tabla <i data-lucide="crosshair"></i>
            </button>
          `;
        } else {
          card.innerHTML = `
            <div class="student-card-info">
              <h4>${est.nombres_apellidos}</h4>
              <p><strong>Cédula / CUP:</strong> ${est.cedula} | ${est.numero_unico}</p>
              <p><strong>Carrera:</strong> ${est.carrera} (${est.grupo})</p>
              <p><strong>Sede:</strong> ${est.sede}</p>
            </div>
            <button class="btn-marcar-asistencia-card" data-ident="${ident}">
              Marcar Asistencia <i data-lucide="check-circle"></i>
            </button>
          `;
        }
        resultsContainer.appendChild(card);
      });

      if (window.lucide) lucide.createIcons();

      // Botón Ubicar en Tabla para estudiantes que ya tienen asistencia
      resultsContainer.querySelectorAll(".btn-ubicar-en-tabla-card").forEach(btn => {
        btn.addEventListener("click", (ev) => {
          ev.stopPropagation();
          const asistId = ev.currentTarget.getAttribute("data-asist-id");
          const nombre = ev.currentTarget.getAttribute("data-nombre") || "Estudiante";

          if (asistId) {
            selectedAsistenciaIds.clear();
            selectedAsistenciaIds.add(asistId);
            updateAsistenciaSeleccionUI();

            const row = document.querySelector(`tr[data-asist-id="${asistId}"]`);
            if (row) {
              row.scrollIntoView({ behavior: "smooth", block: "center" });
            }

            resultsContainer.style.display = "none";
            showToast(`ℹ️ "${nombre}" ya está registrado en la lista de asistencia.`);
          }
        });
      });

      // Agregar evento click a botones de marcar asistencia
      resultsContainer.querySelectorAll(".btn-marcar-asistencia-card").forEach(btn => {
        btn.addEventListener("click", async (ev) => {
          ev.stopPropagation();
          if (!isAsistenciaAbierta) {
            showToast("🔒 La toma de asistencias está cerrada para esta actividad.");
            return;
          }
          const idToMark = ev.currentTarget.getAttribute("data-ident");
          if (idToMark) {
            const resAsist = await ejecutarRegistroAsistencia(idToMark);
            if (resAsist && resAsist.success) {
              showToast(`✅ Asistencia marcada para ${resAsist.asistente.nombre}`);
              resultsContainer.style.display = "none";
              if (escanerInput) escanerInput.value = "";
              await loadEventAndAttendance();
            } else {
              showToast(`⚠️ ${resAsist ? resAsist.message : "Error al registrar asistencia"}`);
            }
          }
        });
      });
    } else {
      resultsContainer.innerHTML = `
        <div style='color: #f87171; grid-column: 1/-1; text-align: center; padding: 12px;'>
          No se encontraron estudiantes con los filtros especificados.
        </div>
      `;
    }
  }

  let searchDebounceTimer = null;

  if (escanerInput) {
    setTimeout(() => escanerInput.focus(), 300);

    // Búsqueda en tiempo real al escribir (UX mejorada con debounce de 250ms)
    escanerInput.addEventListener("input", () => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        procesarBusquedaFiltrada();
      }, 250);
    });

    escanerInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        clearTimeout(searchDebounceTimer);
        procesarEscaneo();
      }
    });
  }

  if (btnEscanerSubmit) {
    btnEscanerSubmit.addEventListener("click", (e) => {
      e.preventDefault();
      clearTimeout(searchDebounceTimer);
      procesarBusquedaFiltrada();
    });
  }

  // Eventos de cambio en los selectores de filtro
  document.getElementById("filter-carrera-select")?.addEventListener("change", () => procesarBusquedaFiltrada());
  document.getElementById("filter-grupo-select")?.addEventListener("change", () => procesarBusquedaFiltrada());

  // Formateadores y Validadores en Vivo para Estudiante Nuevo
  const nuevoCedulaEl = document.getElementById("nuevo-cedula");
  if (nuevoCedulaEl) {
    // La letra de la cédula y los guiones son intocables.
    nuevoCedulaEl.addEventListener("keydown", (e) => {
      if (e.key === "Backspace") {
        const selStart = nuevoCedulaEl.selectionStart;
        const val = nuevoCedulaEl.value;
        if (val.length === 16 && selStart === 16) {
          e.preventDefault();
          let rawDigits = val.replace(/[^0-9]/g, "");
          let truncated = rawDigits.slice(0, -1);
          let formatted = "";
          if (truncated.length > 0) formatted += truncated.slice(0, Math.min(3, truncated.length));
          if (truncated.length > 3) formatted += "-" + truncated.slice(3, Math.min(9, truncated.length));
          if (truncated.length > 9) formatted += "-" + truncated.slice(9, Math.min(13, truncated.length));
          nuevoCedulaEl.value = formatted;
        } else if (selStart > 0 && val[selStart - 1] === "-") {
          e.preventDefault();
          const newVal = val.slice(0, selStart - 2) + val.slice(selStart);
          nuevoCedulaEl.value = newVal;
          nuevoCedulaEl.dispatchEvent(new Event("input"));
        }
      }
    });

    nuevoCedulaEl.addEventListener("input", (e) => {
      let raw = e.target.value.toUpperCase();
      let digits = raw.replace(/[^0-9]/g, "");
      if (digits.length > 13) digits = digits.slice(0, 13);

      let formatted = "";
      if (digits.length > 0) formatted += digits.slice(0, Math.min(3, digits.length));
      if (digits.length > 3) formatted += "-" + digits.slice(3, Math.min(9, digits.length));
      if (digits.length > 9) formatted += "-" + digits.slice(9, Math.min(13, digits.length));

      // Algoritmo oficial de Cédula Nicaragüense Módulo 23 (Letra intocable autogenerada)
      if (digits.length === 13) {
        const LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y"];
        const letter = LETTERS[parseInt(digits, 10) % 23];
        if (letter) formatted += letter;
      }

      e.target.value = formatted;
    });
  }

  // Formateador de Carné Estudiantil (0000-0000X: Guiones intocables, números y letra editables)
  const nuevoCarnetEl = document.getElementById("nuevo-carnet");
  if (nuevoCarnetEl) {
    nuevoCarnetEl.addEventListener("keydown", (e) => {
      if (e.key === "Backspace") {
        const selStart = nuevoCarnetEl.selectionStart;
        const val = nuevoCarnetEl.value;
        if (selStart > 0 && val[selStart - 1] === "-") {
          e.preventDefault();
          const newVal = val.slice(0, selStart - 2) + val.slice(selStart);
          nuevoCarnetEl.value = newVal;
          nuevoCarnetEl.dispatchEvent(new Event("input"));
        }
      }
    });

    nuevoCarnetEl.addEventListener("input", (e) => {
      let raw = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
      let digits = raw.replace(/[^0-9]/g, "");
      let letter = raw.replace(/[^A-Z]/g, "").slice(0, 1);

      if (digits.length > 8) digits = digits.slice(0, 8);

      let formatted = "";
      if (digits.length > 0) formatted += digits.slice(0, Math.min(4, digits.length));
      if (digits.length > 4) formatted += "-" + digits.slice(4, 8);
      if (digits.length >= 8 && letter) formatted += letter;

      e.target.value = formatted;
    });
  }

  const nuevoNupEl = document.getElementById("nuevo-nup");
  if (nuevoNupEl) {
    nuevoNupEl.addEventListener("input", (e) => {
      e.target.value = e.target.value.toUpperCase().replace(/[^A-Z0-9-]/g, "");
    });
  }

  const nuevoNombreEl = document.getElementById("nuevo-nombre");
  if (nuevoNombreEl) {
    nuevoNombreEl.addEventListener("input", (e) => {
      e.target.value = e.target.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "");
    });
  }

  // Formateador y guía dinámica interactiva de Grupo [ATN-XXX-XXX] (Guiones intocables)
  const nuevoGrupoEl = document.getElementById("nuevo-grupo");
  if (nuevoGrupoEl) {
    nuevoGrupoEl.addEventListener("keydown", (e) => {
      if (e.key === "Backspace") {
        const selStart = nuevoGrupoEl.selectionStart;
        const val = nuevoGrupoEl.value;
        if (selStart > 0 && val[selStart - 1] === "-") {
          e.preventDefault();
          const newVal = val.slice(0, selStart - 2) + val.slice(selStart);
          nuevoGrupoEl.value = newVal;
          nuevoGrupoEl.dispatchEvent(new Event("input"));
        }
      }
    });

    function updateGrupoFormatterAndGuide(e) {
      let raw = e.target.value.toUpperCase().replace(/[^A-Z0-9-]/g, "");

      // 1. Extraer primer trío ATN (Año: 1-5, Turno: M/T/N, Num: 1-9)
      let formatted = "";
      let p1 = "";
      if (raw.length > 0) {
        let char1 = raw[0].replace(/[^1-5]/g, "");
        if (char1) p1 += char1;
      }
      if (raw.length > 1 && p1.length === 1) {
        let char2 = raw[1].replace(/[^MTN]/g, "");
        if (char2) p1 += char2;
      }
      if (raw.length > 2 && p1.length === 2) {
        let char3 = raw[2].replace(/[^1-9]/g, "");
        if (char3) p1 += char3;
      }

      if (p1.length > 0) formatted += p1;

      // Auto-insertar 1er guión tras el trío ATN
      if (p1.length === 3) {
        formatted += "-";
        let rest = raw.slice(3).replace(/^-+/, "");

        if (rest.length > 0) {
          let parts = rest.split("-");
          // Trío 2: Máximo 3 letras para la carrera (evita 4 letras juntas)
          let carreraPart = parts[0].replace(/[^A-Z]/g, "").slice(0, 3);
          formatted += carreraPart;

          // Si el trío 2 tiene 3 letras y hay más caracteres (o guión), auto-insertar 2do guión
          if (carreraPart.length === 3) {
            let restAfterCarrera = rest.slice(carreraPart.length).replace(/^-+/, "");
            if (restAfterCarrera.length > 0 || rest.includes("-")) {
              let sufijo = restAfterCarrera.replace(/[^A-Z0-9]/g, "").slice(0, 3);
              formatted += "-" + sufijo;
            }
          }
        }
      }

      e.target.value = formatted;

      // 2. Guía dinámica de placeholder (ATN-XXX-XXX)
      if (!formatted) {
        nuevoGrupoEl.placeholder = "ATN-XXX-XXX";
      } else {
        let parts = formatted.split("-");
        let trio1 = parts[0] || "";
        let trio2 = parts[1] || "";
        let trio3 = parts[2] || "";

        if (parts.length <= 1) {
          let template1 = "ATN";
          let hint1 = template1.slice(trio1.length);
          nuevoGrupoEl.placeholder = trio1 + hint1 + "-XXX-XXX";
        } else if (parts.length === 2 && trio3.length === 0 && !formatted.endsWith("-")) {
          let hint2 = "XXX".slice(trio2.length);
          nuevoGrupoEl.placeholder = formatted + hint2 + "-XXX";
        } else if (formatted.endsWith("-") && parts.length === 2) {
          nuevoGrupoEl.placeholder = formatted + "XXX";
        } else if (parts.length >= 3 && trio3.length > 0) {
          // Al aparecer la primera letra del 3er trío, la guía de espacios faltantes desaparece
          nuevoGrupoEl.placeholder = formatted;
        }
      }
    }

    nuevoGrupoEl.addEventListener("input", updateGrupoFormatterAndGuide);
  }

  // 8. Botón Estudiante Nuevo (+ Estudiante Nuevo)
  if (btnAbrirNuevo && formNuevo) {
    btnAbrirNuevo.addEventListener("click", () => {
      if (!isAsistenciaAbierta) {
        showToast("🔒 La toma de asistencias está cerrada para esta actividad.");
        if (formNuevo) {
          formNuevo.classList.remove("open");
          formNuevo.style.display = "none";
        }
        return;
      }
      formNuevo.style.display = "";
      formNuevo.classList.toggle("open");
    });
  }

  if (btnCerrarNuevo && formNuevo) {
    btnCerrarNuevo.addEventListener("click", () => {
      formNuevo.classList.remove("open");
    });
  }

  // Cargar catálogos de ciudades para Residencia y Procedencia
  if (typeof API !== "undefined" && API.getCatalogos) {
    API.getCatalogos().then(cat => {
      if (cat && cat.success && cat.ciudades) {
        const resSel = document.getElementById("nuevo-ciudad-residencia");
        const procSel = document.getElementById("nuevo-ciudad-procedencia");
        const opts = '<option value="">Seleccione ciudad...</option>' +
          cat.ciudades.map(c => `<option value="${c.id}">${c.nombre}</option>`).join("");
        if (resSel) resSel.innerHTML = opts;
        if (procSel) procSel.innerHTML = opts;
      }
    }).catch(() => { });
  }

  window.toggleFormPersonaFields = function () {
    const tipo = document.getElementById("nuevo-tipo-persona")?.value || "Estudiante";
    const secEst = document.getElementById("seccion-campos-estudiante");
    const secTrab = document.getElementById("seccion-campos-trabajador");
    if (tipo === "Trabajador") {
      if (secEst) secEst.style.display = "none";
      if (secTrab) secTrab.style.display = "contents";
    } else {
      if (secEst) secEst.style.display = "contents";
      if (secTrab) secTrab.style.display = "none";
    }
  };

  // 9. Guardar Persona Nueva (Estudiante o Trabajador)
  if (btnGuardarNuevo) {
    btnGuardarNuevo.addEventListener("click", async (e) => {
      e.preventDefault();

      if (!isAsistenciaAbierta) {
        showToast("🔒 La toma de asistencias está cerrada para este evento.");
        return;
      }

      const tipo_persona = document.getElementById("nuevo-tipo-persona")?.value || "Estudiante";
      const nup = document.getElementById("nuevo-nup")?.value.trim() || "";
      const cedula = document.getElementById("nuevo-cedula")?.value.trim() || "";
      const nombres_apellidos = document.getElementById("nuevo-nombre")?.value.trim() || "";
      const sexo = document.getElementById("nuevo-sexo")?.value || "Masculino";
      const ciudad_residencia_id = document.getElementById("nuevo-ciudad-residencia")?.value || null;
      const ciudad_procedencia_id = document.getElementById("nuevo-ciudad-procedencia")?.value || null;

      const carnet = document.getElementById("nuevo-carnet")?.value.trim() || "";
      const carrera = document.getElementById("nuevo-carrera")?.value || "Ingeniería de Sistemas";
      const ano_academico = document.getElementById("nuevo-ano")?.value || "1º Año";
      const grupo = document.getElementById("nuevo-grupo")?.value.trim() || "";
      const turno = document.getElementById("nuevo-turno")?.value || "Diurno";

      const codigo_trabajador = document.getElementById("nuevo-codigo-trabajador")?.value.trim() || "";
      const cargo = document.getElementById("nuevo-cargo")?.value.trim() || "";
      const tipo_contrato = document.getElementById("nuevo-tipo-contrato")?.value || "Tiempo Completo";

      if (!nombres_apellidos) {
        showToast("⚠️ Ingrese el nombre completo de la persona (solo letras).");
        return;
      }

      if (nombres_apellidos && !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(nombres_apellidos)) {
        showToast("⚠️ El nombre solo debe contener letras y espacios.");
        return;
      }

      if (cedula) {
        const rawDigits = cedula.replace(/[^0-9]/g, "");
        if (rawDigits.length !== 13) {
          showToast("⚠️ La cédula debe constar de 13 dígitos más la letra verificadora (ej: 001-030704-1067H).");
          return;
        }
        const LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y"];
        const expectedLetter = LETTERS[parseInt(rawDigits, 10) % 23];
        const givenLetter = cedula.slice(-1).toUpperCase();
        if (givenLetter !== expectedLetter) {
          showToast(`⚠️ La letra de la cédula es inválida. La letra calculada es '${expectedLetter}'.`);
          return;
        }
      }

      if (tipo_persona === "Estudiante" && grupo && !/^[1-5][MTN][1-9]-[A-Z]{2,4}(-[A-Z0-9]+)?$/i.test(grupo)) {
        showToast("⚠️ Formato de grupo inválido. Formato requerido: ATN-XXX-X (Ej. 5T1-COM-S o 1M1-ME).");
        return;
      }

      const payload = {
        tipo_persona, nup, cedula, nombres_apellidos, sexo,
        ciudad_residencia_id, ciudad_procedencia_id,
        carnet, carrera, ano_academico, grupo, turno,
        codigo_trabajador, cargo, tipo_contrato,
        evento_id: currentAsistenciaEventId
      };

      const res = await API.registrarPersonaNueva(payload);

      if (res && res.success) {
        showToast(res.message);
        if (formNuevo) formNuevo.classList.remove("open");
        // Limpiar campos del formulario
        ["nuevo-nup", "nuevo-cedula", "nuevo-nombre", "nuevo-carnet", "nuevo-grupo", "nuevo-codigo-trabajador", "nuevo-cargo"].forEach(id => {
          const el = document.getElementById(id);
          if (el) el.value = "";
        });
        await loadEventAndAttendance();
      } else {
        showToast(`⚠️ ${res ? res.message : "Error al registrar persona"}`);
      }
    });
  }

  // Cargar datos iniciales
  await loadEventAndAttendance();
}

document.addEventListener("DOMContentLoaded", () => {
  setupAsistenciaView();
});


/* ==========================================================================
   VISTA DE USUARIOS
   ========================================================================== */
const mockUsers = [
  { id: 1001, name: "Juan Pérez Rodríguez", role: "Docente Titular", dept: "Facultad de Ingeniería", email: "juan.perez@uni.edu.ni", phone: "+505 8000-0001", extra: "Coordinador de tesis y proyectos." },
  { id: 1002, name: "María González López", role: "Administrativo", dept: "Dirección de Registro", email: "maria.gonzalez@uni.edu.ni", phone: "+505 8000-0002", extra: "Encargada de admisiones." },
  { id: 1003, name: "Carlos Martínez Silva", role: "Estudiante Activo", dept: "Facultad de Arquitectura", email: "carlos.martinez@uni.edu.ni", phone: "+505 8000-0003", extra: "Presidente del consejo estudiantil." },
  { id: 1004, name: "Ana Ruiz Fonseca", role: "Investigador", dept: "DACTIC", email: "ana.ruiz@uni.edu.ni", phone: "+505 8000-0004", extra: "Investigadora en innovación tecnológica." },
  { id: 1005, name: "Luis Fernández Castro", role: "Coordinador", dept: "Extensión Universitaria", email: "luis.fernandez@uni.edu.ni", phone: "+505 8000-0005", extra: "Organizador principal de eventos y ferias." }
];

function renderUsers(users) {
  const container = document.getElementById("usuarios-list");
  if (!container) return;

  container.innerHTML = "";

  if (users.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <i data-lucide="users"></i>
        <p>No se encontraron usuarios con ese criterio.</p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  users.forEach(user => {
    const card = document.createElement("div");
    card.className = "user-card";

    card.innerHTML = `
      <div class="user-card-header">
        <div class="user-card-avatar"><i data-lucide="user"></i></div>
        <div class="user-card-name">${user.name} #CUP${user.id}</div>
        <div class="user-card-pills">
          <span class="user-pill">${user.role}</span>
          <span class="user-pill">${user.dept}</span>
        </div>
        <button class="btn-editar-usuario" onclick="handleEditUser(event)">Editar usuario</button>
      </div>
      <div class="user-card-details">
        <p><strong>Email:</strong> ${user.email} | <strong>Teléfono:</strong> ${user.phone}</p>
        <p>${user.extra}</p>
      </div>
    `;
    container.appendChild(card);
  });

  if (window.lucide) lucide.createIcons();
}

function handleEditUser(event) {
  event.stopPropagation();
  event.preventDefault();
  if (typeof showToast === "function") {
    showToast("?? Funcionalidad de edición en desarrollo");
  } else {
    alert("Funcionalidad de edición en desarrollo");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.body.getAttribute("data-page") === "usuarios") {
    renderUsers(mockUsers);

    const searchInput = document.getElementById("user-search-input");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = mockUsers.filter(u =>
          u.name.toLowerCase().includes(term) ||
          u.id.toString().includes(term)
        );
        renderUsers(filtered);
      });
    }
  }
});

/**
 * Activa manualmente una actividad programada:
 * Llama al endpoint POST /api/eventos/<id>/activar y refresca el carrusel sin recargar la página completa.
 * @param {string} id - UUID de la actividad programada a activar.
 */
async function activateActivity(id) {
  if (!id) return;

  if (!confirm("¿Estás seguro de que deseas activar esta actividad ahora?")) return;

  if (typeof API !== "undefined" && API.activarEvento) {
    const res = await API.activarEvento(id);
    if (res && res.success) {
      showToast("✅ Actividad activada exitosamente");
      await renderAllCarousels();
    } else {
      if (typeof ClientCache !== "undefined") ClientCache.invalidateAll();
      showToast(`⚠️ ${res ? res.message : "La actividad ya no existe en la base de datos."}`);
      await renderAllCarousels();
    }
  }
}

async function finalizeActivity(id) {
  if (!id) return;

  if (!confirm("¿Estás seguro de que deseas finalizar esta actividad? Esta acción no se puede deshacer.")) return;

  if (typeof API !== "undefined" && API.finalizarEvento) {
    const res = await API.finalizarEvento(id);
    if (res && res.success) {
      showToast("✅ Actividad finalizada exitosamente");
      setTimeout(() => { window.location.replace("index.html"); }, 1000);
    } else {
      if (typeof ClientCache !== "undefined") ClientCache.invalidateAll();
      showToast(`⚠️ ${res ? res.message : "Error al finalizar actividad"}`);
      await renderAllCarousels();
    }
  }
}

