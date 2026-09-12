class DomainError(Exception):
    """Error base de dominio. Cada subclase define su propio codigo/status."""

    codigo = "DOMAIN_ERROR"
    status_code = 400

    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)


class CoordenadaInvalida(DomainError):
    codigo = "COORDENADA_INVALIDA"
    status_code = 422


class SinRutaEncontrada(DomainError):
    codigo = "SIN_RUTA_ENCONTRADA"
    status_code = 422


class ProveedorNoDisponible(DomainError):
    codigo = "PROVEEDOR_NO_DISPONIBLE"
    status_code = 503
