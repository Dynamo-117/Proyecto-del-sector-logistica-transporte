import { useEffect, useState } from "react";
import { ApiRequestError } from "../api/client";
import { obtenerResumen } from "../api/resumen";
import type { ResumenOperativo } from "../types";

function Indicador({ valor, etiqueta }: { valor: number | string; etiqueta: string }) {
  return (
    <div className="indicador">
      <strong>{valor}</strong>
      <span>{etiqueta}</span>
    </div>
  );
}

function NoDisponible() {
  return <p className="mensaje-error">Servicio no disponible en este momento.</p>;
}

export function ResumenPage() {
  const [resumen, setResumen] = useState<ResumenOperativo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);

  async function cargar() {
    setCargando(true);
    setError(null);
    try {
      setResumen(await obtenerResumen());
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo cargar el resumen");
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    cargar();
  }, []);

  return (
    <div className="pagina">
      <div className="pagina__encabezado">
        <h1>Resumen operativo</h1>
        <button className="boton-secundario" onClick={cargar} disabled={cargando}>
          Actualizar
        </button>
      </div>
      <p className="subtitulo">
        Una sola consulta al gateway (GET /resumen) que reune flota, rutas, mantenimiento y
        tracking.
      </p>

      {error && <p className="mensaje-error">{error}</p>}

      {resumen && (
        <>
          <div className="tarjeta">
            <h2>Flota</h2>
            {resumen.flota.disponible ? (
              <div className="indicadores">
                <Indicador valor={resumen.flota.total_vehiculos} etiqueta="vehiculos" />
                {Object.entries(resumen.flota.vehiculos_por_estado).map(([estado, n]) => (
                  <Indicador key={estado} valor={n} etiqueta={estado} />
                ))}
                <Indicador
                  valor={`${resumen.flota.conductores_disponibles}/${resumen.flota.total_conductores}`}
                  etiqueta="conductores disponibles"
                />
              </div>
            ) : (
              <NoDisponible />
            )}
          </div>

          <div className="tarjeta">
            <h2>Rutas activas</h2>
            {resumen.rutas.disponible ? (
              <div className="indicadores">
                <Indicador valor={resumen.rutas.rutas_activas} etiqueta="rutas" />
                <Indicador
                  valor={`${resumen.rutas.distancia_total_km} km`}
                  etiqueta="distancia total"
                />
              </div>
            ) : (
              <NoDisponible />
            )}
          </div>

          <div className="tarjeta">
            <h2>Mantenimiento</h2>
            {resumen.mantenimiento.disponible ? (
              <div className="indicadores">
                <Indicador valor={resumen.mantenimiento.alertas_activas} etiqueta="alertas activas" />
                <Indicador
                  valor={resumen.mantenimiento.vehiculos_con_alertas}
                  etiqueta="vehiculos con alertas"
                />
              </div>
            ) : (
              <NoDisponible />
            )}
          </div>

          <div className="tarjeta">
            <h2>Tracking</h2>
            {resumen.tracking.disponible ? (
              <div className="indicadores">
                <Indicador valor={resumen.tracking.en_movimiento} etiqueta="en movimiento" />
                <Indicador valor={resumen.tracking.detenidos} etiqueta="detenidos" />
                <Indicador valor={resumen.tracking.sin_telemetria} etiqueta="sin telemetria" />
              </div>
            ) : (
              <NoDisponible />
            )}
          </div>

          <p className="subtitulo">
            Generado con {resumen.llamadas_internas} consultas internas a 4 microservicios, en una
            sola llamada del frontend.
          </p>
        </>
      )}
    </div>
  );
}
