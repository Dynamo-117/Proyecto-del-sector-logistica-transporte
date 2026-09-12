import pytest

from app.domain.exceptions import TokenInvalido
from app.infrastructure.security.jwt_token_service import JWTTokenService
from app.infrastructure.security.password_hasher import BcryptPasswordHasher


def test_bcrypt_password_hasher_verifica_password_correcta():
    hasher = BcryptPasswordHasher()
    hash_generado = hasher.hashear("clave123")

    assert hash_generado != "clave123"
    assert hasher.verificar("clave123", hash_generado) is True
    assert hasher.verificar("otra-clave", hash_generado) is False


def test_jwt_token_service_crea_y_decodifica_token():
    service = JWTTokenService("secreto", "HS256", expire_minutos=60)
    token = service.crear_token("user-id-123", "ADMINISTRADOR")

    payload = service.decodificar_token(token)

    assert payload["sub"] == "user-id-123"
    assert payload["rol"] == "ADMINISTRADOR"


def test_jwt_token_service_rechaza_token_con_firma_invalida():
    service_emisor = JWTTokenService("secreto-a", "HS256")
    service_validador = JWTTokenService("secreto-b", "HS256")
    token = service_emisor.crear_token("user-id-123", "OPERADOR")

    with pytest.raises(TokenInvalido):
        service_validador.decodificar_token(token)


def test_jwt_token_service_rechaza_token_expirado():
    service = JWTTokenService("secreto", "HS256", expire_minutos=-1)
    token = service.crear_token("user-id-123", "OPERADOR")

    with pytest.raises(TokenInvalido):
        service.decodificar_token(token)


def test_jwt_token_service_rechaza_token_malformado():
    service = JWTTokenService("secreto", "HS256")

    with pytest.raises(TokenInvalido):
        service.decodificar_token("esto-no-es-un-jwt")
