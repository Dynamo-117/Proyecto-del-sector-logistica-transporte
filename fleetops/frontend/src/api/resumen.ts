import { apiFetch } from "./client";
import type { ResumenOperativo } from "../types";

export function obtenerResumen(): Promise<ResumenOperativo> {
  return apiFetch<ResumenOperativo>("/resumen");
}
