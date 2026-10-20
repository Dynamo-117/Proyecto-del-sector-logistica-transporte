import { apiFetch } from "./client";
import type { EstadoEventos } from "../types";

export function obtenerEstadoEventos(): Promise<EstadoEventos> {
  return apiFetch<EstadoEventos>("/fleet/eventos/estado");
}

export function reintentarEventos(): Promise<{ entregados: number; pendientes: number }> {
  return apiFetch("/fleet/eventos/reintentar", { method: "POST" });
}
