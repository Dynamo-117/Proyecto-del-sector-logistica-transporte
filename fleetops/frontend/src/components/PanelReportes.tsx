import { useState } from "react";
import { ApiRequestError } from "../api/client";
import {
  guardarArchivo,
  obtenerReporte,
  type FormatoReporte,
  type ReporteGenerado,
  type TipoReporte,
} from "../api/reportes";

interface Props {
  tipos: { valor: TipoReporte; etiqueta: string }[];
}

const FORMATOS: { valor: FormatoReporte; etiqueta: string }[] = [
  { valor: "csv", etiqueta: "CSV (Excel)" },
  { valor: "json", etiqueta: "JSON" },
  { valor: "html", etiqueta: "HTML" },
];

export function PanelReportes({ tipos }: Props) {
  const [tipo, setTipo] = useState<TipoReporte>(tipos[0].valor);
  const [formato, setFormato] = useState<FormatoReporte>("csv");
  const [reporte, setReporte] = useState<ReporteGenerado | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [generando, setGenerando] = useState(false);

  async function generar(descargar: boolean) {
    setGenerando(true);
    setError(null);
    try {
      const generado = await obtenerReporte(tipo, formato);
      setReporte(generado);
      if (descargar) guardarArchivo(generado);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo generar el reporte");
    } finally {
      setGenerando(false);
    }
  }

  return (
    <div className="tarjeta">
      <h2>Reportes</h2>
      <div className="formulario-inline">
        <label>
          Reporte
          <select value={tipo} onChange={(e) => setTipo(e.target.value as TipoReporte)}>
            {tipos.map((t) => (
              <option key={t.valor} value={t.valor}>
                {t.etiqueta}
              </option>
            ))}
          </select>
        </label>
        <label>
          Formato
          <select value={formato} onChange={(e) => setFormato(e.target.value as FormatoReporte)}>
            {FORMATOS.map((f) => (
              <option key={f.valor} value={f.valor}>
                {f.etiqueta}
              </option>
            ))}
          </select>
        </label>
        <button className="boton-secundario" onClick={() => generar(false)} disabled={generando}>
          Vista previa
        </button>
        <button onClick={() => generar(true)} disabled={generando}>
          Descargar
        </button>
      </div>

      {error && <p className="mensaje-error">{error}</p>}

      {reporte && (
        <div className="vista-previa">
          <p className="subtitulo">Archivo: {reporte.nombreArchivo}</p>
          {reporte.mediaType.startsWith("text/html") ? (
            <iframe title="Vista previa del reporte" srcDoc={reporte.contenido} sandbox="" />
          ) : (
            <pre>{reporte.contenido}</pre>
          )}
        </div>
      )}
    </div>
  );
}
