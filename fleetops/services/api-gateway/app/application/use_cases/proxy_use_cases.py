from __future__ import annotations

from app.application.ports.proxy import ProxyClient, RespuestaBackend
from app.domain.exceptions import ServicioNoRegistrado


class ReenviarPeticion:
    """Resuelve el prefijo de la ruta contra el mapa de servicios registrados
    y reenvia la peticion tal cual (metodo, headers, query params y cuerpo) al
    servicio destino, devolviendo su respuesta sin transformarla."""

    def __init__(self, proxy_client: ProxyClient, rutas_servicios: dict[str, str]):
        self._proxy_client = proxy_client
        self._rutas_servicios = rutas_servicios

    async def ejecutar(
        self,
        prefijo: str,
        resto_path: str,
        method: str,
        headers: dict[str, str],
        params: dict[str, str],
        content: bytes,
    ) -> RespuestaBackend:
        base_url = self._rutas_servicios.get(prefijo)
        if base_url is None:
            raise ServicioNoRegistrado(
                f"No hay ningun servicio registrado bajo el prefijo '{prefijo}'"
            )

        url = f"{base_url}/{resto_path}" if resto_path else base_url
        return await self._proxy_client.enviar(method, url, headers, params, content)
