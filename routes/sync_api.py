"""
===============================================================================
EVENTOS-UNI - API REST DE SINCRONIZACIÓN Y RECONCILIACIÓN DISTRIBUIDA (`/api/v1/sync`)
===============================================================================
Proporciona los endpoints RESTful para:
- POST /api/v1/sync                : Sincronización transaccional batch (Push & Pull).
- GET  /api/v1/sync/status         : Historial y estado de lotes de sincronización.
- GET  /api/v1/sync/conflicts      : Consulta de colisiones y discrepancias de versión.
- POST /api/v1/sync/resolve        : Arbitraje y resolución de conflictos de concurrencia.
- POST /api/v1/sync/nodes/register : Alta y autorización de nuevas terminales de campo.
- GET  /api/v1/sync/nodes          : Consulta del estado de los nodos clientes del clúster.
===============================================================================
"""

import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session
from database import db
from models.base import Usuario
from models.catalogos import Sede
from models.sync import (
    NodoCliente,
    LoteSincronizacion,
    ConflictoSincronizacion,
    BitacoraAccion
)
from core.security import login_required, roles_required, verify_token_and_restore_session
from core.sync_engine import SyncEngine

sync_bp = Blueprint("sync_api", __name__)


# -----------------------------------------------------------------------------
# 1. POST /api/v1/sync - Endpoint Nuclear de Sincronización Batch
# -----------------------------------------------------------------------------

@sync_bp.route("/sync", methods=["POST"])
def sync_batch():
    """
    Recibe un lote de eventos, asistencias, personas y tombstones desde una terminal de campo.
    Ejecuta la reconciliación transaccional (UPSERT) y retorna el delta de cambios del servidor.
    
    Headers opcionales para handshake de hardware:
      - X-Node-Mac: Dirección MAC de la terminal
      - X-Node-ApiKey: Clave de autenticación del nodo
    """
    # 1. Autenticar origen (por token de usuario o por handshake de hardware)
    user_authenticated = verify_token_and_restore_session()
    usuario_id = session.get("user_id") if user_authenticated else None

    mac_address = request.headers.get("X-Node-Mac") or (request.json and request.json.get("mac_address"))
    api_key = request.headers.get("X-Node-ApiKey") or (request.json and request.json.get("api_key", ""))

    nodo = None
    if mac_address:
        nodo = SyncEngine.authenticate_node(mac_address, api_key)

    # Si no hay nodo registrado pero hay usuario autenticado, buscar o autovincular
    if not nodo and user_authenticated:
        usuario = Usuario.query.get(usuario_id)
        # Buscar el primer nodo activo de la sede del usuario o nodo por defecto
        sede_default = Sede.query.first()
        sede_id = sede_default.id if sede_default else str(uuid.uuid4())
        
        nodo = NodoCliente.query.filter_by(nombre_equipo=f"Terminal-{usuario.email[:8]}").first()
        if not nodo:
            nodo = NodoCliente(
                id=str(uuid.uuid4()),
                sede_id=sede_id,
                nombre_equipo=f"Terminal-{usuario.email[:8]}",
                mac_adress=mac_address or f"VIRTUAL-{uuid.uuid4().hex[:12].upper()}",
                api_key_hash="default-node-key",
                estado_activo=True
            )
            db.session.add(nodo)
            db.session.commit()

    if not nodo:
        return jsonify({
            "success": False,
            "message": "Terminal no autorizada. Proporcione cabeceras válidas X-Node-Mac y X-Node-ApiKey o autentíquese con un usuario."
        }), 401

    payload = request.get_json() or {}
    ip_origen = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")

    # 2. Procesar el lote mediante el SyncEngine
    resultado = SyncEngine.process_sync_batch(
        nodo=nodo,
        usuario_id=usuario_id,
        payload=payload,
        ip_origen=ip_origen
    )

    status_code = 200 if resultado.get("success") else 500
    return jsonify(resultado), status_code


# -----------------------------------------------------------------------------
# 2. GET /api/v1/sync/status - Historial y Estado de Lotes de Sincronización
# -----------------------------------------------------------------------------

@sync_bp.route("/sync/status", methods=["GET"])
@login_required
def get_sync_status():
    """
    Retorna los últimos lotes de sincronización procesados en el clúster central.
    """
    limit = int(request.args.get("limit", 20))
    lotes = LoteSincronizacion.query.order_by(LoteSincronizacion.timestamp_recepcion.desc()).limit(limit).all()

    data = []
    for l in lotes:
        data.append({
            "id": l.id,
            "nodo_id": l.nodos_cliente_id,
            "nodo_nombre": l.nodo_cliente.nombre_equipo if l.nodo_cliente else "Desconocido",
            "sede": l.nodo_cliente.sede.nombre if l.nodo_cliente and l.nodo_cliente.sede else "N/A",
            "total_registros": l.total_registros,
            "estado": l.estado_procesamiento,
            "timestamp": l.timestamp_recepcion,
            "conflictos": len(l.conflictos)
        })

    return jsonify({
        "success": True,
        "total_lotes": len(data),
        "lotes": data
    }), 200


# -----------------------------------------------------------------------------
# 3. GET /api/v1/sync/conflicts - Consulta de Conflictos Pendientes
# -----------------------------------------------------------------------------

@sync_bp.route("/sync/conflicts", methods=["GET"])
@login_required
@roles_required("Rector", "Encargado")
def get_conflicts():
    """
    Lista las colisiones de concurrencia pendientes de resolución.
    """
    estado = request.args.get("estado", "PENDIENTE")
    query = ConflictoSincronizacion.query
    if estado:
        query = query.filter_by(estado_resolucion=estado)

    conflictos = query.order_by(ConflictoSincronizacion.id.desc()).all()
    data = []
    for c in conflictos:
        data.append({
            "id": c.id,
            "lote_id": c.lote_id,
            "tabla_afectada": c.tabla_afectada,
            "registro_id_conflicto": c.registro_id_conflicto,
            "tipo_conflicto": c.tipo_conflicto,
            "payload_local": c.payload_local,
            "payload_servidor": c.payload_servidor,
            "estado_resolucion": c.estado_resolucion,
            "resuelto_por": c.resuelto_por.email if c.resuelto_por else None
        })

    return jsonify({
        "success": True,
        "total_conflictos": len(data),
        "conflictos": data
    }), 200


# -----------------------------------------------------------------------------
# 4. POST /api/v1/sync/resolve - Resolución Manual de Conflictos
# -----------------------------------------------------------------------------

@sync_bp.route("/sync/resolve", methods=["POST"])
@login_required
@roles_required("Rector")
def resolve_conflict():
    """
    Aplica el arbitraje de un conflicto:
    - 'RESUELTO_LOCAL': Sobrescribe los datos del servidor con la copia del cliente.
    - 'RESUELTO_SERVIDOR': Conserva la versión del servidor y descarta el cambio local.
    """
    data = request.get_json()
    if not data or not data.get("conflicto_id") or not data.get("decision"):
        return jsonify({"success": False, "message": "Datos incompletos"}), 400

    conflicto = ConflictoSincronizacion.query.get(data["conflicto_id"])
    if not conflicto:
        return jsonify({"success": False, "message": "Conflicto no encontrado"}), 404

    decision = data["decision"]  # 'RESUELTO_LOCAL' | 'RESUELTO_SERVIDOR'
    usuario_id = session.get("user_id")

    if decision not in ["RESUELTO_LOCAL", "RESUELTO_SERVIDOR"]:
        return jsonify({"success": False, "message": "Decisión no válida"}), 400

    conflicto.estado_resolucion = decision
    conflicto.resuelto_por_usuario_id = usuario_id

    # Registrar en la bitácora
    bitacora = BitacoraAccion(
        id=str(uuid.uuid4()),
        usuario_id=usuario_id,
        direccion_ip=request.remote_addr or "127.0.0.1",
        accion_realizada=f"RESOLVER_CONFLICTO_{decision}",
        tabla_afectada=conflicto.tabla_afectada,
        registro_id_afectado=conflicto.registro_id_conflicto,
        datos_nuevos={"decision": decision, "conflicto_id": conflicto.id}
    )
    db.session.add(bitacora)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Conflicto {conflicto.id} resuelto como {decision}"
    }), 200


# -----------------------------------------------------------------------------
# 5. POST /api/v1/sync/nodes/register - Registro de Nodos de Campo
# -----------------------------------------------------------------------------

@sync_bp.route("/sync/nodes/register", methods=["POST"])
@login_required
@roles_required("Rector")
def register_node():
    """
    Da de alta una nueva terminal de campo autorizada en el clúster central.
    """
    data = request.get_json()
    if not data or not data.get("mac_address") or not data.get("nombre_equipo") or not data.get("sede_id"):
        return jsonify({"success": False, "message": "Faltan campos obligatorios (mac_address, nombre_equipo, sede_id)"}), 400

    mac = data["mac_address"].strip()
    existente = NodoCliente.query.filter_by(mac_adress=mac).first()
    if existente:
        return jsonify({"success": False, "message": "Ya existe un nodo con esta dirección MAC"}), 409

    api_key_plain = data.get("api_key") or str(uuid.uuid4())
    nuevo_nodo = NodoCliente(
        id=str(uuid.uuid4()),
        sede_id=data["sede_id"],
        nombre_equipo=data["nombre_equipo"].strip(),
        mac_adress=mac,
        api_key_hash=api_key_plain,
        estado_activo=True
    )
    db.session.add(nuevo_nodo)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Nodo de campo registrado exitosamente",
        "nodo": {
            "id": nuevo_nodo.id,
            "nombre_equipo": nuevo_nodo.nombre_equipo,
            "mac_address": nuevo_nodo.mac_adress,
            "api_key": api_key_plain,
            "sede_id": nuevo_nodo.sede_id
        }
    }), 201


# -----------------------------------------------------------------------------
# 6. GET /api/v1/sync/nodes - Consulta de Nodos Registrados
# -----------------------------------------------------------------------------

@sync_bp.route("/sync/nodes", methods=["GET"])
@login_required
def list_nodes():
    """
    Retorna la lista de terminales y su estado de conectividad/sincronización.
    """
    nodos = NodoCliente.query.all()
    data = []
    for n in nodos:
        data.append({
            "id": n.id,
            "nombre_equipo": n.nombre_equipo,
            "mac_address": n.mac_adress,
            "sede": n.sede.nombre if n.sede else "N/A",
            "estado_activo": n.estado_activo,
            "ultima_sincronizacion": n.ultima_sincronizacion
        })

    return jsonify({
        "success": True,
        "total_nodos": len(data),
        "nodos": data
    }), 200
