import { useState, type FormEvent } from "react";
import { ApiRequestError } from "../api/client";
import { calcularRuta } from "../api/navigation";
import type { RutaCalculada } from "../types";

export function NavigationPage() {
  const [latOrigen, setLatOrigen] = useState("4.71");
  const [lonOrigen, setLonOrigen] = useState("-74.07");
  const [latDestino, setLatDestino] = useState("6.25");
  const [lonDestino, setLonDestino] = useState("-75.56");
  const [resultado, setResultado] = useState<RutaCalculada | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [calculando, setCalculando] = useState(false);

  async function handleCalcular(evento: FormEvent) {
    evento.preventDefault();
    setCalculando(true);
    setError(null);
    setResultado(null);
    try {
      const ruta = await calcularRuta(
        { latitud: Number(latOrigen), longitud: Number(lonOrigen) },
        { latitud: Number(latDestino), longitud: Number(lonDestino) },
      );
      setResultado(ruta);
    } catch (err) {
      setError(
        err instanceof ApiRequestError
          ? err.message
          : "No se pudo calcular la ruta (revisa la conexion a internet: usa el servidor publico de OSRM)",
      );
    } finally {
      setCalculando(false);
    }
  }

  return (
    <div className="pagina">
      <h1>Calcular ruta (OSRM)</h1>
      <p className="subtitulo">
        navigation-integration-service consulta el servidor publico de OSRM en tiempo real; requiere
        salida a internet.
      </p>

      <form className="tarjeta formulario-inline" onSubmit={handleCalcular}>
        <label>
          Origen (lat)
          <input
            type="number"
            step="0.0001"
            value={latOrigen}
            onChange={(e) => setLatOrigen(e.target.value)}
            required
          />
        </label>
        <label>
          Origen (lon)
          <input
            type="number"
            step="0.0001"
            value={lonOrigen}
            onChange={(e) => setLonOrigen(e.target.value)}
            required
          />
        </label>
        <label>
          Destino (lat)
          <input
            type="number"
            step="0.0001"
            value={latDestino}
            onChange={(e) => setLatDestino(e.target.value)}
            required
          />
        </label>
        <label>
          Destino (lon)
          <input
            type="number"
            step="0.0001"
            value={lonDestino}
            onChange={(e) => setLonDestino(e.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={calculando}>
          {calculando ? "Calculando..." : "Calcular ruta"}
        </button>
      </form>

      {error && <p className="mensaje-error">{error}</p>}

      {resultado && (
        <div className="tarjeta">
          <h2>Resultado</h2>
          <p>
            <strong>{resultado.distancia_km.toFixed(1)} km</strong> —{" "}
            {resultado.duracion_min.toFixed(1)} min — {resultado.puntos.length} puntos en la
            geometria de la ruta.
          </p>
        </div>
      )}
    </div>
  );
}
