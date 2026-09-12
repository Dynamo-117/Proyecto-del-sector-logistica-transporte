from collections.abc import Mapping

HEADERS_SALTO_A_SALTO = {"connection", "keep-alive", "transfer-encoding"}
HEADERS_A_EXCLUIR_DE_LA_PETICION = HEADERS_SALTO_A_SALTO | {
    "host",
    "content-length",
    "x-correlation-id",
}


def filtrar_headers_salientes(headers: Mapping[str, str]) -> dict[str, str]:
    return {k: v for k, v in headers.items() if k.lower() not in HEADERS_SALTO_A_SALTO}


def filtrar_headers_entrantes(headers: Mapping[str, str], correlation_id: str) -> dict[str, str]:
    filtrados = {
        k: v for k, v in headers.items() if k.lower() not in HEADERS_A_EXCLUIR_DE_LA_PETICION
    }
    filtrados["x-correlation-id"] = correlation_id
    return filtrados
