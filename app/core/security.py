from pwdlib import PasswordHash


class PasswordHasher:
    _password_hash = PasswordHash.recommended()

    def get_password_hash(self, password: str) -> str:
        return self._password_hash.hash(password)

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        return self._password_hash.verify(plain_password, hashed_password)
