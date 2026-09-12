import { apiFetch } from "./client";
import type { Conexion, Nodo, RutaOptimizada } from "../types";

export function listarNodos(): Promise<Nodo[]> {
  return apiFetch<Nodo[]>("/routing/nodos");
}

export interface NodoCreatePayload {
  nombre: string;
  latitud: number;
  longitud: number;
}

export function crearNodo(payload: NodoCreatePayload): Promise<Nodo> {
  return apiFetch<Nodo>("/routing/nodos", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function crearConexion(
  nodoOrigenId: string,
  nodoDestinoId: string,
  distanciaKm: number,
): Promise<Conexion> {
  return apiFetch<Conexion>(`/routing/nodos/${nodoOrigenId}/conexiones`, {
    method: "POST",
    body: JSON.stringify({ nodo_destino_id: nodoDestinoId, distancia_km: distanciaKm }),
  });
}

export interface SolicitudCargaPayload {
  origen_nodo_id: string;
  destino_nodo_id: string;
  peso_kg: number;
  volumen_m3: number;
}

export function solicitarAsignacion(payload: SolicitudCargaPayload): Promise<RutaOptimizada> {
  return apiFetch<RutaOptimizada>("/routing/cargas", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listarRutas(): Promise<RutaOptimizada[]> {
  return apiFetch<RutaOptimizada[]>("/routing/rutas");
}
