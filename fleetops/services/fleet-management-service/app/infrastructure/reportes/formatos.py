from __future__ import annotations

import csv
import io
import json
from html import escape

from app.application.reportes.formato_reporte import FormatoReporte


class FormatoCSV(FormatoReporte):
    media_type = "text/csv; charset=utf-8"
    extension = "csv"

    def render(self, titulo: str, columnas: list[str], filas: list[list[str]]) -> str:
        salida = io.StringIO()
        escritor = csv.writer(salida, lineterminator="\n")
        escritor.writerow(columnas)
        escritor.writerows(filas)
        return "﻿" + salida.getvalue()


class FormatoJSON(FormatoReporte):
    media_type = "application/json"
    extension = "json"

    def render(self, titulo: str, columnas: list[str], filas: list[list[str]]) -> str:
        documento = {
            "titulo": titulo,
            "total": len(filas),
            "filas": [dict(zip(columnas, fila, strict=True)) for fila in filas],
        }
        return json.dumps(documento, ensure_ascii=False, indent=2)


class FormatoHTML(FormatoReporte):
    media_type = "text/html; charset=utf-8"
    extension = "html"

    def render(self, titulo: str, columnas: list[str], filas: list[list[str]]) -> str:
        cabecera = "".join(f"<th>{escape(c)}</th>" for c in columnas)
        cuerpo = "".join(
            "<tr>" + "".join(f"<td>{escape(celda)}</td>" for celda in fila) + "</tr>"
            for fila in filas
        )
        return (
            '<!doctype html><html lang="es"><head><meta charset="utf-8">'
            f"<title>{escape(titulo)}</title>"
            "<style>body{font-family:Segoe UI,Arial,sans-serif;margin:24px;color:#1a1a1a}"
            "table{border-collapse:collapse;min-width:420px}"
            "th{background:#1f4e5f;color:#fff;text-align:left}"
            "th,td{border:1px solid #c8c8c8;padding:6px 12px}</style></head><body>"
            f"<h2>{escape(titulo)}</h2><p>{len(filas)} registro(s)</p>"
            f"<table><thead><tr>{cabecera}</tr></thead><tbody>{cuerpo}</tbody></table>"
            "</body></html>"
        )


FORMATOS: dict[str, FormatoReporte] = {
    "csv": FormatoCSV(),
    "json": FormatoJSON(),
    "html": FormatoHTML(),
}
