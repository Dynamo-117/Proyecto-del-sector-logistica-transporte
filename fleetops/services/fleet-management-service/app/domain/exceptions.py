class DomainError(Exception):
    """Error base de dominio. Cada subclase define su propio codigo/status."""

    codigo = "DOMAIN_ERROR"
    status_code = 400

    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)


class VehiculoNoEncontrado(DomainError):
    codigo = "VEHICULO_NO_ENCONTRADO"
    status_code = 404


class ConductorNoEncontrado(DomainError):
    codigo = "CONDUCTOR_NO_ENCONTRADO"
    status_code = 404


class PlacaDuplicada(DomainError):
    codigo = "PLACA_DUPLICADA"
    status_code = 409


class LicenciaDuplicada(DomainError):
    codigo = "LICENCIA_DUPLICADA"
    status_code = 409


class VehiculoYaAsignado(DomainError):
    codigo = "VEHICULO_YA_ASIGNADO"
    status_code = 409


class ConductorYaAsignado(DomainError):
    codigo = "CONDUCTOR_YA_ASIGNADO"
    status_code = 409


class ConductorNoDisponible(DomainError):
    codigo = "CONDUCTOR_NO_DISPONIBLE"
    status_code = 409


class VehiculoNoDisponible(DomainError):
    codigo = "VEHICULO_NO_DISPONIBLE"
    status_code = 409


class UsuarioNoEncontrado(DomainError):
    codigo = "USUARIO_NO_ENCONTRADO"
    status_code = 404


class EmailDuplicado(DomainError):
    codigo = "EMAIL_DUPLICADO"
    status_code = 409


class CredencialesInvalidas(DomainError):
    codigo = "CREDENCIALES_INVALIDAS"
    status_code = 401


class UsuarioInactivo(DomainError):
    codigo = "USUARIO_INACTIVO"
    status_code = 403


class TokenInvalido(DomainError):
    codigo = "TOKEN_INVALIDO"
    status_code = 401
