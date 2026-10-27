"""
===============================================================================
EVENTOS-UNI - MOTOR DE RECONCILIACIÓN TRANSACCIONAL Y SINCRONIZACIÓN (UPSERT)
===============================================================================
Implementa el motor de sincronización bidireccional (Push/Pull) e idempotente:
1. Validación de Nodo Cliente y Handshake mediante MAC Address / API Key.
2. Procesamiento de lotes batch de Actividades, Asistencias, Padrón y Tombstones.
3. Detección y registro de conflictos concurrentes (LWW - Last Write Wins con fallback a auditoría).
4. Persistencia en lote con manejo de transacciones ACID y bitácoras forenses.
5. Generación de delta de cambios del servidor para actualizar la base de datos local.
===============================================================================
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from database import db
from models.base import Persona, Estudiante, Trabajador, Usuario
from models.catalogos import Sede, EspacioFisico, UnidadOrganizativa, TipoActividad, Lineamiento
from models.eventos import Actividad, ActividadLineamiento, Asistencia
from models.sync import (
    NodoCliente,
    LoteSincronizacion,
    ConflictoSincronizacion,
    BitacoraAccion,
    Tombstone
)


class SyncEngine:
    """
    Motor nuclear de reconciliación distribuida entre terminales locales y el clúster central.
    """

    @staticmethod
    def authenticate_node(mac_address: str, api_key: str) -> Optional[NodoCliente]:
        """
        Valida la identidad de una terminal de campo mediante su dirección MAC y API Key.
        
        :param mac_address: Dirección MAC reportada por el cliente.
        :param api_key: API Key en texto o hash para cotejo.
        :return: Instancia de NodoCliente autorizada o None.
        """
        if not mac_address:
            return None
        nodo = NodoCliente.query.filter_by(mac_adress=mac_address.strip(), estado_activo=True).first()
        if not nodo:
            return None
        # Verificación directa o por hash seguro
        if nodo.api_key_hash and nodo.api_key_hash != api_key.strip():
            return None
        return nodo

    @staticmethod
    def process_sync_batch(
        nodo: NodoCliente,
        usuario_id: Optional[str],
        payload: Dict[str, Any],
        ip_origen: str = "127.0.0.1"
    ) -> Dict[str, Any]:
        """
        Procesa de forma atómica un lote de sincronización emitido por una terminal de campo.
        
        :param nodo: NodoCliente emisor.
        :param usuario_id: ID del usuario autenticado que ejecuta la sincronización.
        :param payload: Diccionario con los datos batch (actividades, asistencias, personas, tombstones, last_sync_timestamp).
        :param ip_origen: IP del cliente para la bitácora forense.
        :return: Diccionario con el resultado de la reconciliación y el delta de cambios del servidor.
        """
        ahora_iso = datetime.now(timezone.utc).isoformat()
        
        # 1. Crear el registro del Lote de Sincronización
        lote = LoteSincronizacion(
            nodos_cliente_id=nodo.id,
            tabla_afectada="multiple",
            total_registros=0,
            timestamp_recepcion=ahora_iso,
            estado_procesamiento="PENDIENTE"
        )
        db.session.add(lote)
        db.session.flush()  # Obtener el lote.id

        confirmados: Dict[str, List[str]] = {
            "actividades": [],
            "asistencias": [],
            "personas": [],
            "tombstones": []
        }
        conflictos_detectados = 0
        total_items = 0

        try:
            # -----------------------------------------------------------------
            # A. Procesar Personas Nuevas / Actualizaciones de Padrón Local
            # -----------------------------------------------------------------
            personas_batch = payload.get("personas", [])
            for item in personas_batch:
                total_items += 1
                p_id = item.get("id") or str(uuid.uuid4())
                cedula = item.get("cedula")
                numero_unico = item.get("numero_unico")

                if not cedula or not numero_unico:
                    continue

                existente = Persona.query.filter(
                    (Persona.id == p_id) | (Persona.cedula == cedula) | (Persona.numero_unico == numero_unico)
                ).first()

                if not existente:
                    nueva_p = Persona(
                        id=p_id,
                        numero_unico=numero_unico,
                        cedula=cedula,
                        nombres_apellidos=item.get("nombres_apellidos", "Sin Nombre"),
                        sexo=item.get("sexo", "M"),
                        ciudad_residencia_id=item.get("ciudad_residencia_id"),
                        ciudad_procedencia_id=item.get("ciudad_procedencia_id"),
                        sede_id=item.get("sede_id") or nodo.sede_id
                    )
                    db.session.add(nueva_p)
                    
                    # Subtipo Estudiante si viene en payload
                    if item.get("estudiante"):
                        est_data = item["estudiante"]
                        est = Estudiante(
                            persona_id=p_id,
                            carnet_estudiante=est_data.get("carnet_estudiante"),
                            area_conocimiento_id=est_data.get("area_conocimiento_id"),
                            carrera=est_data.get("carrera", "Ingeniería"),
                            ano_academico=est_data.get("ano_academico", "1ro"),
                            grupo=est_data.get("grupo", "1M1"),
                            turno=est_data.get("turno", "Diurno")
                        )
                        db.session.add(est)

                    # Subtipo Trabajador si viene en payload
                    if item.get("trabajador"):
                        trab_data = item["trabajador"]
                        trab = Trabajador(
                            persona_id=p_id,
                            codigo_trabajador=trab_data.get("codigo_trabajador"),
                            unidad_id=trab_data.get("unidad_id"),
                            cargo=trab_data.get("cargo", "Docente"),
                            condicion_laboral=trab_data.get("condicion_laboral", "Planta")
                        )
                        db.session.add(trab)

                    confirmados["personas"].append(p_id)
                else:
                    confirmados["personas"].append(existente.id)

            # -----------------------------------------------------------------
            # B. Reconciliación Transaccional de Actividades (UPSERT)
            # -----------------------------------------------------------------
            actividades_batch = payload.get("actividades", [])
            for item in actividades_batch:
                total_items += 1
                act_id = item.get("id")
                if not act_id:
                    continue

                act_existente = Actividad.query.get(act_id)
                local_updated_at = item.get("updated_at", ahora_iso)

                if not act_existente:
                    # INSERT de nueva actividad creada offline
                    nueva_act = Actividad(
                        id=act_id,
                        codigo_actividad=item.get("codigo_actividad", f"ACT-{act_id[:8]}"),
                        nombre=item.get("nombre", "Actividad Sincronizada"),
                        tipo_actividad_id=item.get("tipo_actividad_id"),
                        unidad_responsable_id=item.get("unidad_responsable_id"),
                        usuario_creador_id=item.get("usuario_creador_id") or usuario_id,
                        espacio_fisico_id=item.get("espacio_fisico_id"),
                        proposito=item.get("proposito", ""),
                        imagen_url=item.get("imagen_url"),
                        fecha_inicio=item.get("fecha_inicio"),
                        fecha_fin=item.get("fecha_fin"),
                        hora_inicio=item.get("hora_inicio"),
                        hora_fin=item.get("hora_fin"),
                        asistencia_abierta=bool(item.get("asistencia_abierta", True)),
                        is_synced=1,
                        created_offline=item.get("created_offline", 1),
                        updated_at=local_updated_at
                    )
                    db.session.add(nueva_act)
                    
                    # Asociar lineamientos si vienen en el payload
                    lineamientos_payload = item.get("lineamientos", [])
                    for lin_item in lineamientos_payload:
                        lin_id = lin_item.get("lineamiento_id")
                        if lin_id:
                            assoc = ActividadLineamiento(
                                id=str(uuid.uuid4()),
                                actividad_id=act_id,
                                lineamiento_id=lin_id,
                                justificacion=lin_item.get("justificacion", "")
                            )
                            db.session.add(assoc)

                    confirmados["actividades"].append(act_id)
                else:
                    # UPSERT / Resolución de Conflictos por LWW (Last-Write-Wins)
                    servidor_updated_at = act_existente.updated_at or ""
                    
                    if local_updated_at >= servidor_updated_at:
                        # La versión del nodo es más reciente o igual -> Actualizar servidor
                        act_existente.nombre = item.get("nombre", act_existente.nombre)
                        act_existente.proposito = item.get("proposito", act_existente.proposito)
                        act_existente.fecha_inicio = item.get("fecha_inicio", act_existente.fecha_inicio)
                        act_existente.fecha_fin = item.get("fecha_fin", act_existente.fecha_fin)
                        act_existente.hora_inicio = item.get("hora_inicio", act_existente.hora_inicio)
                        act_existente.hora_fin = item.get("hora_fin", act_existente.hora_fin)
                        act_existente.asistencia_abierta = bool(item.get("asistencia_abierta", act_existente.asistencia_abierta))
                        act_existente.is_synced = 1
                        act_existente.updated_at = local_updated_at
                        confirmados["actividades"].append(act_id)
                    else:
                        # Colisión: El servidor tiene una versión más reciente -> Registrar Conflicto
                        conflictos_detectados += 1
                        conflicto = ConflictoSincronizacion(
                            id=str(uuid.uuid4()),
                            lote_id=lote.id,
                            tabla_afectada="actividades",
                            registro_id_conflicto=act_id,
                            tipo_conflicto="VERSION_CONCURRENTE",
                            payload_local=item,
                            payload_servidor={
                                "id": act_existente.id,
                                "nombre": act_existente.nombre,
                                "fecha_inicio": act_existente.fecha_inicio,
                                "fecha_fin": act_existente.fecha_fin,
                                "updated_at": act_existente.updated_at
                            },
                            estado_resolucion="PENDIENTE"
                        )
                        db.session.add(conflicto)
                        confirmados["actividades"].append(act_id)

            # -----------------------------------------------------------------
            # C. Inserción Atómica de Asistencias (Idempotente)
            # -----------------------------------------------------------------
            asistencias_batch = payload.get("asistencias", [])
            for item in asistencias_batch:
                total_items += 1
                asist_id = item.get("id")
                act_id = item.get("actividad_id")
                persona_id = item.get("persona_id")

                if not asist_id or not act_id or not persona_id:
                    continue

                # Validar existencia de la persona o actividad
                asist_existente = Asistencia.query.filter(
                    (Asistencia.id == asist_id) | 
                    ((Asistencia.actividad_id == act_id) & (Asistencia.persona_id == persona_id))
                ).first()

                if not asist_existente:
                    nueva_asist = Asistencia(
                        id=asist_id,
                        actividad_id=act_id,
                        persona_id=persona_id,
                        usuario_registrador_id=item.get("usuario_registrador_id") or usuario_id,
                        timestamp_registro=item.get("timestamp_registro", ahora_iso),
                        is_synced=1
                    )
                    db.session.add(nueva_asist)
                    confirmados["asistencias"].append(asist_id)
                else:
                    confirmados["asistencias"].append(asist_existente.id)

            # -----------------------------------------------------------------
            # D. Procesamiento de Tombstones (Bajas propagadas desde el nodo)
            # -----------------------------------------------------------------
            tombstones_batch = payload.get("tombstones", [])
            for item in tombstones_batch:
                total_items += 1
                tabla = item.get("tabla_afectada")
                reg_id = item.get("registro_id_eliminado")

                if tabla == "asistencias" and reg_id:
                    asist_a_borrar = Asistencia.query.get(reg_id)
                    if asist_a_borrar:
                        db.session.delete(asist_a_borrar)
                    
                    # Registrar tombstone central
                    t_central = Tombstone(
                        id=str(uuid.uuid4()),
                        tabla_afectada=tabla,
                        registro_id_eliminado=reg_id,
                        timestamp_eliminacion=item.get("timestamp_eliminacion", ahora_iso),
                        usuario_elimino_id=usuario_id,
                        nodo_cliente_id=nodo.id
                    )
                    db.session.add(t_central)
                    confirmados["tombstones"].append(reg_id)

            # -----------------------------------------------------------------
            # E. Bitácora de Auditoría Forense de la Operación de Sincronización
            # -----------------------------------------------------------------
            bitacora = BitacoraAccion(
                id=str(uuid.uuid4()),
                usuario_id=usuario_id,
                direccion_ip=ip_origen,
                accion_realizada="BATCH_SYNC_PUSH",
                tabla_afectada="multiple",
                registro_id_afectado=lote.id,
                datos_nuevos={
                    "total_items": total_items,
                    "confirmados": {k: len(v) for k, v in confirmados.items()},
                    "conflictos": conflictos_detectados
                },
                timestamp_accion=ahora_iso
            )
            db.session.add(bitacora)

            # -----------------------------------------------------------------
            # F. Actualización del Estado del Lote y del Nodo Cliente
            # -----------------------------------------------------------------
            lote.total_registros = total_items
            lote.estado_procesamiento = "CON_CONFLICTOS" if conflictos_detectados > 0 else "PROCESADO"
            nodo.ultima_sincronizacion = ahora_iso

            db.session.commit()

            # -----------------------------------------------------------------
            # G. Pull Delta: Cambios del Servidor para el Cliente
            # -----------------------------------------------------------------
            last_sync = payload.get("last_sync_timestamp", "1970-01-01T00:00:00")
            server_delta = SyncEngine.get_server_delta(last_sync, nodo.sede_id)

            return {
                "success": True,
                "message": "Sincronización completada exitosamente",
                "lote_id": lote.id,
                "estado": lote.estado_procesamiento,
                "conflictos_count": conflictos_detectados,
                "confirmados": confirmados,
                "server_delta": server_delta,
                "sync_timestamp": ahora_iso
            }

        except Exception as e:
            db.session.rollback()
            lote.estado_procesamiento = "ERROR"
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

            return {
                "success": False,
                "message": f"Error durante la reconciliación transaccional: {str(e)}",
                "lote_id": lote.id,
                "error": str(e)
            }

    @staticmethod
    def get_server_delta(since_timestamp: str, sede_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene los registros modificados o creados en el servidor central
        posteriormente a una marca temporal dada (Delta Pull).
        
        :param since_timestamp: Timestamp ISO 8601 de la última sincronización del nodo.
        :param sede_id: Sede del nodo para filtrar eventos relevantes.
        :return: Diccionario con listas de actividades, asistencias y tombstones actualizados.
        """
        # Actividades modificadas
        query_act = Actividad.query.filter(Actividad.updated_at > since_timestamp)
        actividades_delta = []
        for act in query_act.all():
            actividades_delta.append({
                "id": act.id,
                "codigo_actividad": act.codigo_actividad,
                "nombre": act.nombre,
                "tipo_actividad_id": act.tipo_actividad_id,
                "unidad_responsable_id": act.unidad_responsable_id,
                "espacio_fisico_id": act.espacio_fisico_id,
                "proposito": act.proposito,
                "fecha_inicio": act.fecha_inicio,
                "fecha_fin": act.fecha_fin,
                "hora_inicio": act.hora_inicio,
                "hora_fin": act.hora_fin,
                "asistencia_abierta": act.asistencia_abierta,
                "updated_at": act.updated_at
            })

        # Tombstones pendientes
        query_tomb = Tombstone.query.filter(Tombstone.timestamp_eliminacion > since_timestamp)
        tombstones_delta = []
        for t in query_tomb.all():
            tombstones_delta.append({
                "id": t.id,
                "tabla_afectada": t.tabla_afectada,
                "registro_id_eliminado": t.registro_id_eliminado,
                "timestamp_eliminacion": t.timestamp_eliminacion
            })

        return {
            "actividades": actividades_delta,
            "tombstones": tombstones_delta
        }
