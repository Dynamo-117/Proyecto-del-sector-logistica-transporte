import { apiFetch } from "./client";
import type { Conductor } from "../types";

export function listarConductores(): Promise<Conductor[]> {
  return apiFetch<Conductor[]>("/fleet/conductores");
}

export interface ConductorCreatePayload {
  nombre: string;
  licencia: string;
}

export function crearConductor(payload: ConductorCreatePayload): Promise<Conductor> {
  return apiFetch<Conductor>("/fleet/conductores", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function eliminarConductor(id: string): Promise<void> {
  return apiFetch<void>(`/fleet/conductores/${id}`, { method: "DELETE" });
}
