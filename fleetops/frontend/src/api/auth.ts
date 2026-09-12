import { apiFetch } from "./client";
import type { Usuario } from "../types";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export function login(email: string, password: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/fleet/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function obtenerUsuarioActual(): Promise<Usuario> {
  return apiFetch<Usuario>("/fleet/auth/me");
}
