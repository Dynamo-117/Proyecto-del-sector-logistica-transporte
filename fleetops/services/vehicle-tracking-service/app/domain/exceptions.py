class DomainError(Exception):
    """Error base de dominio. Cada subclase define su propio codigo/status."""

    codigo = "DOMAIN_ERROR"
    status_code = 400

    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)


class VehiculoDesconocido(DomainError):
    codigo = "VEHICULO_DESCONOCIDO"
    status_code = 404


class TelemetriaInvalida(DomainError):
    codigo = "TELEMETRIA_INVALIDA"
    status_code = 422


class TelemetriaNoDisponible(DomainError):
    codigo = "TELEMETRIA_NO_DISPONIBLE"
    status_code = 404
