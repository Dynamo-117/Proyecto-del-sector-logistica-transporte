class DomainError(Exception):
    """Error base de dominio. Cada subclase define su propio codigo/status."""

    codigo = "DOMAIN_ERROR"
    status_code = 400

    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)


class NodoNoEncontrado(DomainError):
    codigo = "NODO_NO_ENCONTRADO"
    status_code = 404


class RutaNoEncontrada(DomainError):
    codigo = "RUTA_NO_ENCONTRADA"
    status_code = 404


class AristaInvalida(DomainError):
    codigo = "ARISTA_INVALIDA"
    status_code = 422


class SinRutaEnGrafo(DomainError):
    codigo = "SIN_RUTA_EN_GRAFO"
    status_code = 422


class SinVehiculoDisponible(DomainError):
    codigo = "SIN_VEHICULO_DISPONIBLE"
    status_code = 409
