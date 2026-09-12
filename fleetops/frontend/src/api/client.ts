export const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8080";

const TOKEN_KEY = "fleetops_token";

export function obtenerToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function guardarToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function borrarToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiRequestError extends Error {
  status: number;
  codigo: string;

  constructor(status: number, codigo: string, mensaje: string) {
    super(mensaje);
    this.name = "ApiRequestError";
    this.status = status;
    this.codigo = codigo;
  }
}

interface CuerpoError {
  codigo?: string;
  mensaje?: string;
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = obtenerToken();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const respuesta = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (respuesta.status === 204) {
    return undefined as T;
  }

  const cuerpo = await respuesta.json().catch(() => null);

  if (!respuesta.ok) {
    const error = cuerpo as CuerpoError | null;
    throw new ApiRequestError(
      respuesta.status,
      error?.codigo ?? "ERROR_DESCONOCIDO",
      error?.mensaje ?? "Ocurrio un error inesperado al hablar con el servidor",
    );
  }

  return cuerpo as T;
}

/**
 * Se suscribe a un endpoint de Server-Sent Events con autenticacion.
 *
 * El EventSource nativo del navegador no permite enviar headers
 * (no hay forma de mandarle Authorization: Bearer <token>), y todas las
 * rutas del gateway requieren ese header. Por eso este lector hace un
 * fetch normal (que si acepta headers) y parsea el stream "data: ...\n\n"
 * manualmente en vez de usar EventSource.
 *
 * Devuelve una funcion para cancelar la suscripcion.
 */
export function suscribirseSSE(
  path: string,
  onMensaje: (data: string) => void,
  onError?: (error: unknown) => void,
): () => void {
  const controller = new AbortController();

  (async () => {
    try {
      const token = obtenerToken();
      const headers = new Headers();
      if (token) headers.set("Authorization", `Bearer ${token}`);

      const respuesta = await fetch(`${BASE_URL}${path}`, {
        headers,
        signal: controller.signal,
      });
      if (!respuesta.ok || !respuesta.body) {
        throw new Error(`No se pudo abrir el stream (status ${respuesta.status})`);
      }

      const reader = respuesta.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const bloques = buffer.split("\n\n");
        buffer = bloques.pop() ?? "";

        for (const bloque of bloques) {
          const linea = bloque.split("\n").find((l) => l.startsWith("data: "));
          if (linea) onMensaje(linea.slice("data: ".length));
        }
      }
    } catch (error) {
      if (!controller.signal.aborted) onError?.(error);
    }
  })();

  return () => controller.abort();
}
