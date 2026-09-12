from app.api.header_utils import filtrar_headers_entrantes, filtrar_headers_salientes


def test_filtrar_headers_entrantes_excluye_host_y_content_length():
    headers = {"Host": "gateway.local", "Content-Length": "42", "Content-Type": "application/json"}

    resultado = filtrar_headers_entrantes(headers, correlation_id="abc-123")

    assert "host" not in {k.lower() for k in resultado}
    assert "content-length" not in {k.lower() for k in resultado}
    assert resultado["Content-Type"] == "application/json"
    assert resultado["x-correlation-id"] == "abc-123"


def test_filtrar_headers_entrantes_sobreescribe_correlation_id_existente():
    headers = {"X-Correlation-Id": "viejo"}

    resultado = filtrar_headers_entrantes(headers, correlation_id="nuevo")

    assert resultado["x-correlation-id"] == "nuevo"


def test_filtrar_headers_salientes_excluye_headers_de_salto_a_salto():
    headers = {
        "Connection": "keep-alive",
        "Transfer-Encoding": "chunked",
        "Content-Type": "text/plain",
    }

    resultado = filtrar_headers_salientes(headers)

    assert resultado == {"Content-Type": "text/plain"}
