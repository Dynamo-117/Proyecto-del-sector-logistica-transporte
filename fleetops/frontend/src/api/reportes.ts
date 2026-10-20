import { ApiRequestError, BASE_URL, obtenerToken } from "./client";

export type TipoReporte = "vehiculos" | "conductores" | "resumen";
export type FormatoReporte = "csv" | "json" | "html";

export interface ReporteGenerado {
  contenido: string;
  nombreArchivo: string;
  mediaType: string;
}

export async function obtenerReporte(
  tipo: TipoReporte,
  formato: FormatoReporte,
): Promise<ReporteGenerado> {
  const token = obtenerToken();
  const headers = new Headers();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const respuesta = await fetch(`${BASE_URL}/fleet/reportes/${tipo}?formato=${formato}`, {
    headers,
  });

  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => null);
    throw new ApiRequestError(
      respuesta.status,
      cuerpo?.codigo ?? "ERROR_DESCONOCIDO",
      cuerpo?.mensaje ?? "No se pudo generar el reporte",
    );
  }

  return {
    contenido: await respuesta.text(),
    nombreArchivo: `${tipo}.${formato}`,
    mediaType: respuesta.headers.get("content-type") ?? "text/plain",
  };
}

export function guardarArchivo(reporte: ReporteGenerado): void {
  const url = URL.createObjectURL(new Blob([reporte.contenido], { type: reporte.mediaType }));
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = reporte.nombreArchivo;
  enlace.click();
  URL.revokeObjectURL(url);
}
