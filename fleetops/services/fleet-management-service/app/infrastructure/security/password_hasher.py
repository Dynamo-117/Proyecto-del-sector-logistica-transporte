from passlib.context import CryptContext

_contexto = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher:
    def hashear(self, password: str) -> str:
        return _contexto.hash(password)

    def verificar(self, password: str, password_hash: str) -> bool:
        return _contexto.verify(password, password_hash)
