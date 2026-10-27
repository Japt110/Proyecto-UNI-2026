/* ==========================================================================
   EVENTOS-UNI - CLIENTE DE API RESTFUL (VANILLA JS ES6)
   ==========================================================================
   Módulo de abstracción HTTP que conecta la interfaz de usuario Vanilla JS
   con los endpoints REST de Flask mediante peticiones asíncronas (fetch API).
   ========================================================================== */

const API_BASE = '/api';

function getStoredToken() {
  try {
    return sessionStorage.getItem('uni_session_token') || localStorage.getItem('uni_session_token');
  } catch (_) {
    return null;
  }
}

function setStoredToken(token) {
  try {
    if (token) {
      sessionStorage.setItem('uni_session_token', token);
      localStorage.setItem('uni_session_token', token);
    }
  } catch (_) {}
}

function clearStoredToken() {
  try {
    sessionStorage.removeItem('uni_session_token');
    localStorage.removeItem('uni_session_token');
  } catch (_) {}
}

/**
 * Wrapper de fetch que adjunta las cabeceras de autorización por token (Bearer / X-Session-Token)
 * a todas las peticiones salientes para mantener la sesión autenticada sin requerir logins constantes.
 */
function fetchWithAuth(url, options = {}) {
  const token = getStoredToken();
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
    headers.set('X-Session-Token', token);
  }
  return fetch(url, { ...options, headers });
}

/* ==========================================================================
   CACHÉ DE SESIÓN DEL CLIENTE (sessionStorage-backed Request Cache)
   ==========================================================================
   Previene peticiones HTTP redundantes al backend cuando múltiples funciones
   (carruseles, filtros, navegación entre páginas) solicitan los mismos datos.

   Estrategia:
   - Persistencia: usa sessionStorage → el caché sobrevive navegaciones entre
     páginas HTML dentro de la misma pestaña del navegador.
   - TTL (Time-To-Live) por tipo de recurso con verificación en cada lectura.
   - Deduplicación de peticiones en vuelo (in-flight): si ya hay una petición
     en curso para la misma key, se reutiliza la misma Promise (memoria local).
   - Invalidación quirúrgica: las mutaciones eliminan sólo las claves afectadas,
     sin destruir datos no relacionados (e.g. catálogos al registrar asistencia).
   - Prefijo de namespace para evitar colisiones con otras claves de sessionStorage.
   ========================================================================== */
const ClientCache = (() => {
  const NS       = 'uni_cache::';   // Namespace prefix
  const _inflight = {};             // { key: Promise } — peticiones en vuelo (sólo en memoria)
  // Los timestamps de revalidación en background se persisten en sessionStorage (clave __bg__<key>)
  // para que sobrevivan a los cambios de página HTML dentro de la misma pestaña del navegador.

  const TTL = {
    auth:      30 * 60 * 1000,    // 30 minutos (la sesión Flask dura 8h)
    eventos:   10 * 1000,         // 10 segundos — auto-revalidación rápida para prevenir datos estancados
    evento_id: 10 * 1000,         // 10 segundos
    catalogos:  2 * 60 * 60 * 1000, // 2 horas — datos casi estáticos
    stats:     10 * 60 * 1000,    // 10 minutos — se invalida al registrar asistencia
  };

  /* ------------------------------------------------------------------
     Operaciones de bajo nivel sobre sessionStorage
     ------------------------------------------------------------------ */

  function _ssGet(key) {
    try {
      const raw = sessionStorage.getItem(NS + key);
      if (!raw) return null;
      const entry = JSON.parse(raw);
      if (Date.now() > entry.expiresAt) {
        sessionStorage.removeItem(NS + key);
        return null;
      }
      return entry.data;
    } catch (_) {
      return null;
    }
  }

  function _ssSet(key, data, ttlMs) {
    try {
      sessionStorage.setItem(NS + key, JSON.stringify({
        data,
        expiresAt: Date.now() + ttlMs,
        cachedAt:  Date.now()
      }));
      _setBgTs(key);
    } catch (e) {
      // sessionStorage lleno (cuota excedida): limpiar entradas expiradas e intentar de nuevo
      _purgeExpired();
      try {
        sessionStorage.setItem(NS + key, JSON.stringify({ data, expiresAt: Date.now() + ttlMs, cachedAt: Date.now() }));
        _setBgTs(key);
      }
      catch (_) { /* silently ignore — degradación a sin caché */ }
    }
  }

  function _ssDel(key) {
    try {
      const target = NS + key;
      Object.keys(sessionStorage).forEach(k => {
        if (k === target || k.startsWith(target)) {
          sessionStorage.removeItem(k);
        }
      });
      Object.keys(localStorage).forEach(k => {
        if (k === target || k.startsWith(target)) {
          localStorage.removeItem(k);
        }
      });
    } catch (_) {}
    _delBgTs(key);
    delete _inflight[key];
  }

  /** Lee el timestamp de la última revalidación en background para una clave (persiste entre páginas). */
  function _getBgTs(key) {
    try {
      const raw = sessionStorage.getItem(NS + '__bg__' + key);
      return raw ? parseInt(raw, 10) : 0;
    } catch (_) { return 0; }
  }

  /** Guarda el timestamp de la última revalidación en background para una clave. */
  function _setBgTs(key) {
    try { sessionStorage.setItem(NS + '__bg__' + key, String(Date.now())); } catch (_) {}
  }

  /** Elimina el timestamp de revalidación en background (se llama cuando se invalida el caché). */
  function _delBgTs(key) {
    try { sessionStorage.removeItem(NS + '__bg__' + key); } catch (_) {}
  }

  /** Elimina del sessionStorage todas las entradas expiradas del namespace. */
  function _purgeExpired() {
    try {
      const now = Date.now();
      Object.keys(sessionStorage)
        .filter(k => k.startsWith(NS))
        .forEach(k => {
          try {
            const entry = JSON.parse(sessionStorage.getItem(k));
            if (now > entry.expiresAt) sessionStorage.removeItem(k);
          } catch (_) { sessionStorage.removeItem(k); }
        });
    } catch (_) {}
  }

  /* ------------------------------------------------------------------
     API Pública
     ------------------------------------------------------------------ */

  /**
   * Invalida claves específicas del caché (invalidación quirúrgica).
   * @param {...string} keys - Claves a invalidar (sin prefijo NS).
   */
  function invalidate(...keys) {
    keys.forEach(k => {
      _ssDel(k);
      _delBgTs(k);
    });
  }

  /**
   * Invalida todo el caché del cliente (ante mutaciones globales o logout explícito).
   */
  function invalidateAll() {
    try {
      Object.keys(sessionStorage)
        .filter(k => k.startsWith(NS))
        .forEach(k => sessionStorage.removeItem(k));
      Object.keys(localStorage)
        .filter(k => k.startsWith(NS))
        .forEach(k => localStorage.removeItem(k));
    } catch (_) {}
    Object.keys(_inflight).forEach(k => delete _inflight[k]);
  }

  /**
   * Notifica al usuario sobre inconsistencia de datos vía Toast y consola.
   * @param {string} reason - Motivo específico del fallo de sincronización.
   * @param {boolean} hasCache - Indica si existen datos locales en caché como respaldo.
   */
  /**
   * Notifica al usuario sobre inconsistencia de datos vía Toast y consola.
   * Silencia automáticamente cualquier error derivado de falta de autenticación/sesión.
   * @param {string} reason - Motivo específico del fallo de sincronización.
   * @param {boolean} hasCache - Indica si existen datos locales en caché como respaldo.
   */
  function _notifyInconsistency(reason, hasCache) {
    if (!reason) return;
    const lower = String(reason).toLowerCase();
    if (lower.includes("401") || lower.includes("403") || lower.includes("sesión no iniciada") || lower.includes("acceso denegado")) {
      return; // Omitir Toast para errores de sesión/autenticación
    }
    const fallbackText = hasCache ? ' Mostrando datos locales en caché.' : '';
    const message = `⚠️ Advertencia de inconsistencia de datos: ${reason}.${fallbackText}`;
    console.warn(message);

    if (typeof window !== 'undefined' && typeof window.showToast === 'function') {
      window.showToast(message);
    }
  }

  /**
   * Revalida los datos con la BD (Pull) en cada consulta.
   * Flujo de sincronización de datos:
   * 1. Si hay caché válida → la devuelve de inmediato (sin petición HTTP).
   *    Luego lanza un pull en background para detectar cambios en la BD.
   *    Si hay cambios, actualiza el caché silenciosamente.
   * 2. Si no hay caché (primera carga o expirada) → hace el pull de red
   *    de forma bloqueante, guarda el resultado y lo devuelve.
   * 3. Si el pull falla (offline, error 5xx, etc.) y hay caché disponible
   *    → devuelve el caché y emite advertencia de inconsistencia.
   * @param {string}   key     - Clave única del recurso en caché.
   * @param {Function} fetchFn - Función async que realiza el pull desde la API REST.
   * @param {number}   ttlMs  - Duración del caché en milisegundos.
   */
  async function getOrFetch(key, fetchFn, ttlMs) {
    const cached = _ssGet(key);

    // ── CASO 1: Caché válida disponible ──────────────────────────────────────
    // Devolver los datos en caché de inmediato para evitar peticiones HTTP redundantes.
    // Lanzar un pull en background SOLO si ha pasado al menos ttlMs/2 desde la última
    // revalidación. El timestamp se persiste en sessionStorage para sobrevivir cambios de página.
    if (cached !== null) {
      const now = Date.now();
      const lastBg = _getBgTs(key);          // Persiste entre páginas HTML de la misma pestaña
      const isEmptyArray = Array.isArray(cached) && cached.length === 0;
      const minInterval = isEmptyArray ? 5000 : (ttlMs / 2); // Si está vacío, revalidar a los 5s para detectar datos nuevos

      if (!_inflight[key + '__bg'] && (now - lastBg) > minInterval) {
        _setBgTs(key); // Marcar inmediatamente para evitar disparos paralelos entre páginas
        _inflight[key + '__bg'] = (async () => {
          try {
            const freshData = await fetchFn();
            if (freshData !== null && freshData !== undefined) {
              const cachedJson = JSON.stringify(cached);
              const freshJson  = JSON.stringify(freshData);
              if (cachedJson !== freshJson) {
                // Hay cambios en la BD → actualizar caché silenciosamente
                _ssSet(key, freshData, ttlMs);
                // Si cambió la lista de eventos y estamos en la página del dashboard, re-renderizar carruseles dinámicamente
                if (key === 'eventos_list' && typeof window !== 'undefined' && typeof window.renderAllCarousels === 'function') {
                  window.renderAllCarousels(freshData);
                }
              } else {
                // Sin cambios → solo refrescar el TTL
                _ssSet(key, cached, ttlMs);
              }
            }
          } catch (err) {
            const isAuthErr = (err && (err.status === 401 || err.status === 403)) ||
                              (err && err.message && (String(err.message).includes("401") || String(err.message).includes("Sesión no iniciada") || String(err.message).includes("Acceso denegado")));
            if (isAuthErr) {
              invalidateAll();
              const path = (typeof window !== 'undefined' && window.location.pathname) ? window.location.pathname.toLowerCase() : "";
              const isLoginPage = path.endsWith("/login") || path.endsWith("/login.html") || path.endsWith("login.html");
              if (!isLoginPage) window.location.replace("login.html");
            }
            // Otros errores en background: silenciar (el usuario ya tiene datos)
          } finally {
            delete _inflight[key + '__bg'];
          }
        })();
      }
      return cached; // ← Retorno inmediato desde caché, sin esperar la red
    }

    // ── CASO 2: Sin caché (primera carga o expirada) ─────────────────────────
    // Reutilizar petición en vuelo si ya se está consultando la misma clave
    if (_inflight[key]) return _inflight[key];

    _inflight[key] = (async () => {
      try {
        const freshData = await fetchFn();

        if (freshData !== null && freshData !== undefined) {
          _ssSet(key, freshData, ttlMs);
          return freshData;
        }

        return freshData;

      } catch (err) {
        const isAuthErr = (err && (err.status === 401 || err.status === 403)) ||
                          (err && err.message && (String(err.message).includes("401") || String(err.message).includes("Sesión no iniciada") || String(err.message).includes("Acceso denegado")));

        if (isAuthErr) {
          invalidateAll();
          const path = (typeof window !== 'undefined' && window.location.pathname) ? window.location.pathname.toLowerCase() : "";
          const isLoginPage = path.endsWith("/login") || path.endsWith("/login.html") || path.endsWith("login.html");
          if (!isLoginPage) {
            window.location.replace("login.html");
          }
          return null;
        }

        let reason = "Error de comunicación con la base de datos";

        if (typeof navigator !== 'undefined' && !navigator.onLine) {
          reason = "Falta de conexión a internet (Modo offline)";
        } else if (err && err.status) {
          if (err.status >= 500) {
            reason = `Error interno del servidor (HTTP ${err.status})`;
          } else if (err.status === 404) {
            reason = "Recurso no encontrado (HTTP 404)";
          } else {
            reason = `Error de respuesta HTTP ${err.status}`;
          }
        } else if (err && err.message) {
          reason = err.message;
        }

        _notifyInconsistency(reason, false);
        return null;

      } finally {
        delete _inflight[key];
      }
    })();

    return _inflight[key];
  }

  /**
   * Actualiza o inserta un evento de manera incremental en la caché local sin borrar todo.
   * @param {Object} evento - Objeto de actividad a agregar o actualizar.
   */
  function upsertEvento(evento) {
    if (!evento || !evento.id) return;

    // 1. Actualizar el listado global 'eventos_list'
    let list = _ssGet('eventos_list');
    if (!Array.isArray(list)) {
      list = [];
    }
    const idx = list.findIndex(e => e.id === evento.id || e.id == evento.id);
    if (idx >= 0) {
      list[idx] = { ...list[idx], ...evento };
    } else {
      list.unshift(evento);
    }
    _ssSet('eventos_list', list, TTL.eventos);

    // 2. Actualizar o crear la entrada de detalle 'evento_<id>'
    let detail = _ssGet(`evento_${evento.id}`);
    if (detail) {
      _ssSet(`evento_${evento.id}`, { ...detail, ...evento }, TTL.evento_id);
    } else {
      _ssSet(`evento_${evento.id}`, evento, TTL.evento_id);
    }
  }

  /**
   * Elimina incrementalmente un evento de la lista y del detalle local sin limpiar la caché global.
   * @param {string} id - UUID del evento a eliminar.
   */
  function removeEvento(id) {
    if (!id) return;

    // 1. Remover del listado 'eventos_list'
    let list = _ssGet('eventos_list');
    if (Array.isArray(list)) {
      list = list.filter(e => e.id !== id && e.id != id);
      _ssSet('eventos_list', list, TTL.eventos);
    } else {
      _ssDel('eventos_list');
    }

    // 2. Borrar entradas individuales
    _ssDel(`evento_${id}`);
    _ssDel(`stats_evento_${id}`);
  }

  return { invalidate, invalidateAll, getOrFetch, upsertEvento, removeEvento, TTL };
})();

function _checkAuthRedirect(response, result) {
  if (response && response.headers) {
    const serverSeed = response.headers.get("X-DB-Seed");
    if (serverSeed) {
      const localSeed = sessionStorage.getItem("uni_db_seed");
      if (localSeed && localSeed !== serverSeed) {
        console.warn("🌱 Base de datos reiniciada en el servidor. Purgando todo el caché local...");
        ClientCache.invalidateAll();
      }
      try { sessionStorage.setItem("uni_db_seed", serverSeed); } catch (_) {}
    }
  }

  const isUnauthorized =
    (response && (response.status === 401 || response.status === 403)) ||
    (result && result.message && (
      String(result.message).includes("Sesión no iniciada") ||
      String(result.message).includes("Acceso denegado") ||
      String(result.message).includes("No autenticado")
    ));

  if (isUnauthorized) {
    ClientCache.invalidateAll();
    clearStoredToken();
    const path = (typeof window !== 'undefined' && window.location.pathname) ? window.location.pathname.toLowerCase() : "";
    const isLoginPage = path.endsWith("/login") || path.endsWith("/login.html") || path.endsWith("login.html");
    if (!isLoginPage) {
      window.location.replace("login.html");
    }
    return true;
  }
  return false;
}

function _parseSessionToken(token) {
  if (!token || typeof token !== "string") return null;
  try {
    const parts = token.split(".");
    if (parts.length < 2) return null;
    const payloadJson = atob(parts[0]);
    const payload = JSON.parse(payloadJson);
    const now = Math.floor(Date.now() / 1000);
    if (payload.exp && now > payload.exp) {
      return null; // Token expirado por límite de tiempo de 8 horas
    }
    return payload;
  } catch (_) {
    return null;
  }
}

/**
 * Objeto global API que encapsula las operaciones HTTP del sistema.
 */
const API = {

  /* ========================================================================
     1. MÓDULO DE AUTENTICACIÓN Y SESIÓN DE USUARIO
     ======================================================================== */

  /**
   * Realiza la autenticación polimórfica de usuario en el sistema.
   * @param {string} identifier - Email, Carné, Cédula o Código de Trabajador.
   * @param {string} password - Contraseña en texto plano.
   * @returns {Promise<Object>} Respuesta JSON del servidor con estado y datos de usuario.
   */
  async login(identifier, password) {
    try {
      // Purgar cualquier caché estática previa de la sesión anterior
      ClientCache.invalidateAll();

      const response = await fetchWithAuth(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, password })
      });
      const result = await response.json();
      if (result.success) {
        ClientCache.invalidateAll(); // Limpieza completa post-login
        if (result.session_token) {
          setStoredToken(result.session_token);
        }
        if (result.user) {
          try {
            sessionStorage.setItem('uni_cache::auth_me', JSON.stringify({
              data: result.user,
              expiresAt: Date.now() + ClientCache.TTL.auth,
              cachedAt: Date.now()
            }));
          } catch (_) {}
        }
      }
      return result;
    } catch (error) {
      console.error('Error de red en login:', error);
      return { success: false, message: 'Error de conexión con el servidor.' };
    }
  },

  /**
   * Cierra la sesión activa en el servidor Flask.
   * @returns {Promise<Object>} Resultado del cierre de sesión.
   */
  async logout() {
    try {
      await fetchWithAuth(`${API_BASE}/auth/logout`, { method: 'POST' });
    } catch (_) {}
    clearStoredToken();
    ClientCache.invalidateAll();
    const path = (typeof window !== 'undefined' && window.location.pathname) ? window.location.pathname.toLowerCase() : "";
    const isLoginPage = path.endsWith("/login") || path.endsWith("/login.html") || path.endsWith("login.html");
    if (!isLoginPage) {
      window.location.replace("login.html");
    }
    return { success: true, message: 'Sesión cerrada correctamente' };
  },

  /**
   * Obtiene la información del usuario autenticado en la sesión actual.
   * Valida el token de sesión almacenado (HMAC con 8 horas de duración).
   * Redirige inmediatamente a login.html si la sesión no es válida.
   * @returns {Promise<Object|null>} Objeto de usuario o null si no está autenticado.
   */
  async getCurrentUser() {
    const token = getStoredToken();
    const tokenPayload = _parseSessionToken(token);

    if (!tokenPayload || !tokenPayload.uid) {
      clearStoredToken();
      ClientCache.invalidateAll();
      const path = (typeof window !== 'undefined' && window.location.pathname) ? window.location.pathname.toLowerCase() : "";
      const isLoginPage = path.endsWith("/login") || path.endsWith("/login.html") || path.endsWith("login.html");
      if (!isLoginPage) {
        window.location.replace("login.html");
      }
      return null;
    }

    try {
      const response = await fetchWithAuth(`${API_BASE}/auth/me`);
      if (response.status === 401 || response.status === 403 || response.status === 404) {
        clearStoredToken();
        ClientCache.invalidateAll();
        const path = (typeof window !== 'undefined' && window.location.pathname) ? window.location.pathname.toLowerCase() : "";
        const isLoginPage = path.endsWith("/login") || path.endsWith("/login.html") || path.endsWith("login.html");
        if (!isLoginPage) {
          window.location.replace("login.html");
        }
        return null;
      }
      const data = await response.json();
      if (data && data.success && data.user) {
        if (data.session_token) setStoredToken(data.session_token);
        return data.user;
      }
    } catch (_) {}

    return {
      id: tokenPayload.uid,
      email: tokenPayload.email,
      role: tokenPayload.role
    };
  },

  /* ========================================================================
     2. MÓDULO DE ACTIVIDADES Y EVENTOS (CRUD)
     ======================================================================== */

  /**
   * Obtiene la lista completa de eventos registrados.
   * Realiza un pull automático de la BD para sincronizar cambios y purgar datos residuales.
   * @returns {Promise<Array>} Arreglo de eventos formateados.
   */
  async getEventos(filters = {}) {
    try {
      const eventos = await ClientCache.getOrFetch(
        'eventos_list',
        async () => {
          const response = await fetchWithAuth(`${API_BASE}/eventos`);
          const data = await response.json();
          if (_checkAuthRedirect(response, data)) throw new Error('HTTP 401');
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          return Array.isArray(data) ? data : (data.eventos || []);
        },
        ClientCache.TTL.eventos
      );

      if (filters && filters.status) {
        return (eventos || []).filter(e => String(e.status).toLowerCase() === String(filters.status).toLowerCase());
      }
      return eventos || [];
    } catch (error) {
      console.error('Error al obtener eventos:', error);
      return [];
    }
  },

  /**
   * Obtiene la información detallada de una actividad específica por su ID UUID.
   * @param {string} id - UUID del evento.
   * @returns {Promise<Object|null>} Datos completos de la actividad o null.
   */
  async getEventoById(id) {
    try {
      return await ClientCache.getOrFetch(
        `evento_${id}`,
        async () => {
          const response = await fetchWithAuth(`${API_BASE}/eventos/${id}`);
          const data = await response.json();
          if (_checkAuthRedirect(response, data)) throw new Error('HTTP 401');
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          return data ? (data.evento || data) : null;
        },
        ClientCache.TTL.evento_id
      );
    } catch (error) {
      console.error('Error al obtener el evento:', error);
      return null;
    }
  },

  /**
   * Registra una nueva actividad en el servidor e inserta incrementalmente en el caché local.
   * @param {Object} eventoData - Datos del formulario de creación.
   * @returns {Promise<Object>} Confirmación de creación.
   */
  async crearEvento(eventoData) {
    try {
      const response = await fetchWithAuth(`${API_BASE}/eventos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventoData)
      });
      const result = await response.json();
      if (_checkAuthRedirect(response, result)) return result;
      if (result.success) {
        ClientCache.invalidate('eventos_list');
      }
      return result;
    } catch (error) {
      console.error('Error al crear evento:', error);
      return { success: false, message: 'Error de red al guardar la actividad.' };
    }
  },

  /**
   * Actualiza parcialmente una actividad existente e invalida la caché local.
   * @param {string} id - UUID del evento.
   * @param {Object} eventoData - Objeto con las propiedades a actualizar.
   * @returns {Promise<Object>} Respuesta de confirmación.
   */
  async updateEvento(id, eventoData) {
    try {
      const response = await fetchWithAuth(`${API_BASE}/eventos/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventoData)
      });
      const result = await response.json();
      if (_checkAuthRedirect(response, result)) return result;
      if (result.success) {
        ClientCache.invalidate('eventos_list', `evento_${id}`);
      }
      return result;
    } catch (error) {
      console.error('Error al actualizar evento:', error);
      return { success: false, message: 'Error de red al actualizar la actividad.' };
    }
  },

  /**
   * Activa manualmente una actividad programada usando el endpoint dedicado.
   * Cambia la fecha de inicio a hoy e invalida la caché local para forzar refresco total.
   * @param {string} id - UUID del evento programado.
   * @returns {Promise<Object>} Respuesta de confirmación con el evento actualizado.
   */
  async activarEvento(id) {
    try {
      const response = await fetchWithAuth(`${API_BASE}/eventos/${id}/activar`, { method: 'POST' });
      const result = await response.json();
      if (_checkAuthRedirect(response, result)) return result;
      ClientCache.invalidate('eventos_list', `evento_${id}`);
      return result;
    } catch (error) {
      console.error('Error al activar evento:', error);
      return { success: false, message: 'Error de red al activar la actividad.' };
    }
  },

  /**
   * Finaliza manualmente una actividad activa usando el endpoint dedicado.
   * Ajusta las fechas a ayer (status pasa a "pasados") e invalida la caché local para forzar refresco total.
   * @param {string} id - UUID del evento activo.
   * @returns {Promise<Object>} Respuesta de confirmación con el evento actualizado.
   */
  async finalizarEvento(id) {
    try {
      const response = await fetchWithAuth(`${API_BASE}/eventos/${id}/finalizar`, { method: 'POST' });
      const result = await response.json();
      if (_checkAuthRedirect(response, result)) return result;
      ClientCache.invalidate('eventos_list', `evento_${id}`);
      return result;
    } catch (error) {
      console.error('Error al finalizar evento:', error);
      return { success: false, message: 'Error de red al finalizar la actividad.' };
    }
  },

  /* ========================================================================
     3. MÓDULO DE TOMA DE ASISTENCIA
     ======================================================================== */

  /**
   * Registra la marca de asistencia de una persona a un evento e invalida el caché.
   * @param {string} eventoId - UUID de la actividad.
   * @param {string} identifier - Carné, Cédula o Código de Trabajador.
   * @returns {Promise<Object>} Resultado del registro de asistencia.
   */
  async registrarAsistencia(eventoId, identifier) {
    try {
      const response = await fetchWithAuth(`${API_BASE}/asistencia/${eventoId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier })
      });
      const result = await response.json();
      if (_checkAuthRedirect(response, result)) return result;
      if (result.success) {
        ClientCache.invalidate('asistencia_', 'eventos_list', 'stats_', 'evento_');
      }
      return result;
    } catch (error) {
      console.error('Error al registrar asistencia:', error);
      return { success: false, message: 'Error de conexión durante el escaneo.' };
    }
  },

  /**
   * Lista todas las personas que han confirmado asistencia en un evento.
   * @param {string} eventoId - UUID de la actividad.
   * @returns {Promise<Array>} Arreglo de personas asistentes.
   */
  async getAsistentesEvento(eventoId) {
    try {
      const response = await fetchWithAuth(`${API_BASE}/asistencia/${eventoId}`);
      const data = await response.json();
      if (_checkAuthRedirect(response, data)) return { success: false, asistentes: [], asistencia_abierta: true };
      if (!response.ok) return { success: false, asistentes: [], asistencia_abierta: true };
      return data;
    } catch (error) {
      console.error('Error al listar asistentes:', error);
      return { success: false, asistentes: [], asistencia_abierta: true };
    }
  },

  /**
   * Conmuta la apertura o cierre de la toma de asistencias para una actividad.
   * @param {string} eventoId - UUID de la actividad.
   * @returns {Promise<Object>} Resultado con el nuevo estado de asistencia_abierta.
   */
  async toggleEstadoAsistencia(eventoId) {
    try {
      const response = await fetchWithAuth(`${API_BASE}/asistencia/${eventoId}/toggle-estado`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const result = await response.json();
      if (_checkAuthRedirect(response, result)) return result;
      if (result.success) {
        ClientCache.invalidate('asistencia_', 'eventos_list', 'stats_', 'evento_');
      }
      return result;
    } catch (error) {
      console.error('Error al conmutar estado de asistencia:', error);
      return { success: false, message: 'Error de conexión al cambiar estado de asistencia.' };
    }
  },

  /**
   * Busca estudiantes en el padrón 5FN aplicando filtros opcionales.
   * @param {Object} params - Objeto con parámetros de filtro (query, cedula, nup, carnet, nombre, carrera, grupo).
   * @returns {Promise<Object>} Resultado de búsqueda con listado de estudiantes.
   */
  async buscarEstudiantes(params = {}) {
    try {
      const queryParams = new URLSearchParams(params).toString();
      const response = await fetchWithAuth(`${API_BASE}/asistencia/buscar-estudiantes?${queryParams}`);
      const result = await response.json();
      if (_checkAuthRedirect(response, result)) return { success: false, estudiantes: [] };
      if (!response.ok) return { success: false, estudiantes: [] };
      return result;
    } catch (error) {
      console.error('Error al buscar estudiantes:', error);
      return { success: false, estudiantes: [] };
    }
  },

  /**
   * Registra una persona nueva (Estudiante o Trabajador) en el padrón 5FN y opcionalmente marca su asistencia.
   * @param {Object} personaData - Datos completos de la persona.
   * @returns {Promise<Object>} Resultado de registro y asistencia.
   */
  async registrarPersonaNueva(personaData) {
    try {
      const response = await fetchWithAuth(`${API_BASE}/asistencia/persona-nueva`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(personaData)
      });
      const result = await response.json();
      if (_checkAuthRedirect(response, result)) return result;
      if (result.success) {
        ClientCache.invalidate('asistencia_', 'eventos_list', 'stats_', 'evento_');
      }
      return result;
    } catch (error) {
      console.error('Error al registrar persona nueva:', error);
      return { success: false, message: 'Error de conexión al registrar persona.' };
    }
  },

  async registrarEstudianteNuevo(studentData) {
    return this.registrarPersonaNueva(studentData);
  },

  /**
   * Elimina un registro de asistencia específico (en caso de error humano).
   * @param {string} asistenciaId - UUID del registro de asistencia.
   * @returns {Promise<Object>} Confirmación de eliminación.
   */
  async eliminarAsistencia(asistenciaId) {
    try {
      const response = await fetchWithAuth(`${API_BASE}/asistencia/${asistenciaId}`, {
        method: 'DELETE'
      });
      const result = await response.json();
      if (_checkAuthRedirect(response, result)) return result;
      if (result.success) {
        ClientCache.invalidateAll();
      }
      return result;
    } catch (error) {
      console.error('Error al eliminar asistencia:', error);
      return { success: false, message: 'Error de conexión al eliminar la asistencia.' };
    }
  },

  /* ========================================================================
     4. MÓDULO DE ESTADÍSTICAS E INDICADORES
     ======================================================================== */

  /**
   * Consulta las estadísticas demográficas de un evento específico.
   * Almacena en caché por 30 segundos.
   * @param {string} eventoId - UUID del evento.
   * @returns {Promise<Object|null>} Métricas demográficas.
   */
  async getStatsEvento(eventoId) {
    try {
      return await ClientCache.getOrFetch(
        `stats_evento_${eventoId}`,
        async () => {
          const response = await fetchWithAuth(`${API_BASE}/stats/evento/${eventoId}`);
          if (!response.ok) {
            const err = new Error(`HTTP ${response.status}`);
            err.status = response.status;
            throw err;
          }
          return await response.json();
        },
        ClientCache.TTL.stats
      );
    } catch (error) {
      console.error('Error al obtener estadísticas del evento:', error);
      return null;
    }
  },

  /**
   * Consulta los indicadores globales para el Dashboard del Rector.
   * Almacena en caché por 30 segundos (clave diferenciada por recinto).
   * @param {string} [recinto=''] - Filtro opcional por código de recinto.
   * @returns {Promise<Object|null>} Resumen institucional global.
   */
  async getStatsGlobales(recinto = '') {
    try {
      const cacheKey = `stats_globales_${recinto}`;
      return await ClientCache.getOrFetch(
        cacheKey,
        async () => {
          const url = recinto
            ? `${API_BASE}/stats/globales?recinto=${encodeURIComponent(recinto)}`
            : `${API_BASE}/stats/globales`;
          const response = await fetchWithAuth(url);
          if (!response.ok) {
            const err = new Error(`HTTP ${response.status}`);
            err.status = response.status;
            throw err;
          }
          return await response.json();
        },
        ClientCache.TTL.stats
      );
    } catch (error) {
      console.error('Error al obtener estadísticas globales:', error);
      return null;
    }
  },

  /* ========================================================================
     5. MÓDULO DE CATÁLOGOS INSTITUCIONALES
     ======================================================================== */

  /**
   * Carga los catálogos base (sedes, espacios, unidades y tipos).
   * Almacena en caché por 10 minutos dado que raramente cambian.
   * @returns {Promise<Object|null>} Objeto con las colecciones de catálogos.
   */
  async getCatalogos() {
    try {
      return await ClientCache.getOrFetch(
        'catalogos',
        async () => {
          const response = await fetchWithAuth(`${API_BASE}/catalogos`);
          if (!response.ok) {
            const err = new Error(`HTTP ${response.status}`);
            err.status = response.status;
            throw err;
          }
          return await response.json();
        },
        ClientCache.TTL.catalogos
      );
    } catch (error) {
      console.error('Error al cargar catálogos:', error);
      return null;
    }
  },

  /* ========================================================================
     6. MÓDULO DE ELIMINACIÓN DE ACTIVIDADES
     ======================================================================== */

  /**
   * Elimina permanentemente una actividad por su UUID.
   * Solo disponible para el rol Rector.
   * El backend bloquea la operación si el evento tiene asistentes registrados
   * o si su status es 'activos' o 'pasados'.
   * @param {string} id - UUID del evento a eliminar.
   * @returns {Promise<Object>} { success, message } del servidor.
   */
  async deleteEvento(id) {
    try {
      const response = await fetchWithAuth(`${API_BASE}/eventos/${id}`, {
        method: 'DELETE'
      });
      const result = await response.json();
      if (_checkAuthRedirect(response, result)) return result;
      if (result.success) {
        ClientCache.invalidate('eventos_list', `evento_${id}`);
      }
      return result;
    } catch (error) {
      console.error('Error al eliminar evento:', error);
      return { success: false, message: 'Error de conexión al intentar eliminar la actividad.' };
    }
  },

  /* ========================================================================
     7. MÓDULO DE CARGA DE ARCHIVOS / IMÁGENES
     ======================================================================== */

  /**
   * Sube una imagen de portada al servidor (/api/uploads/image).
   * @param {File} file - Archivo de imagen a subir.
   * @returns {Promise<Object>} { success, url, message }
   */
  async uploadImage(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetchWithAuth(`${API_BASE}/uploads/image`, {
        method: 'POST',
        body: formData
      });

      return await response.json();
    } catch (error) {
      console.error('Error al subir imagen:', error);
      return { success: false, message: 'Error de red al subir la imagen.' };
    }
  }
};