import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { login as loginRequest, obtenerUsuarioActual } from "../api/auth";
import { borrarToken, guardarToken, obtenerToken } from "../api/client";
import type { Usuario } from "../types";

interface AuthContextValue {
  usuario: Usuario | null;
  token: string | null;
  cargando: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => obtenerToken());
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    if (!token) {
      setUsuario(null);
      setCargando(false);
      return;
    }

    let cancelado = false;
    setCargando(true);
    obtenerUsuarioActual()
      .then((actual) => {
        if (!cancelado) setUsuario(actual);
      })
      .catch(() => {
        if (!cancelado) {
          borrarToken();
          setToken(null);
        }
      })
      .finally(() => {
        if (!cancelado) setCargando(false);
      });

    return () => {
      cancelado = true;
    };
  }, [token]);

  async function login(email: string, password: string) {
    const { access_token } = await loginRequest(email, password);
    guardarToken(access_token);
    setToken(access_token);
    setUsuario(await obtenerUsuarioActual());
  }

  function logout() {
    borrarToken();
    setToken(null);
    setUsuario(null);
  }

  return (
    <AuthContext.Provider value={{ usuario, token, cargando, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  }
  return context;
}
