class DomainError(Exception):
    """Error base de dominio. Cada subclase define su propio codigo/status."""

    codigo = "DOMAIN_ERROR"
    status_code = 400

    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)


class ServicioNoRegistrado(DomainError):
    codigo = "SERVICIO_NO_REGISTRADO"
    status_code = 404


class ServicioNoDisponible(DomainError):
    codigo = "SERVICIO_NO_DISPONIBLE"
    status_code = 502
