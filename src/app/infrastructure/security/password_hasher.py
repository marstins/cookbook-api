from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError


class PasswordHasher:
    def __init__(self) -> None:
        self._ph = Argon2Hasher()

    def hash_password(self, password_string: str) -> str:
        return self._ph.hash(password_string)

    def verify_password(self, password_string: str, password_hash: str) -> bool:
        try:
            self._ph.verify(password_hash, password_string)
            return True
        except VerifyMismatchError:
            return False
