import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { ApiRequestError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function LoginPage() {
  const { token, login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  if (token) {
    return <Navigate to="/vehiculos" replace />;
  }

  async function handleSubmit(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await login(email, password);
      navigate("/vehiculos", { replace: true });
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo conectar con el servidor");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="pagina-login">
      <form className="tarjeta tarjeta-login" onSubmit={handleSubmit}>
        <h1>FleetOps</h1>
        <p className="subtitulo">Inicia sesion para continuar</p>

        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(evento) => setEmail(evento.target.value)}
            autoFocus
            required
          />
        </label>

        <label>
          Contrasena
          <input
            type="password"
            value={password}
            onChange={(evento) => setPassword(evento.target.value)}
            required
          />
        </label>

        {error && <p className="mensaje-error">{error}</p>}

        <button type="submit" disabled={enviando}>
          {enviando ? "Ingresando..." : "Ingresar"}
        </button>
      </form>
    </div>
  );
}
