from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.domain.exceptions import UnauthorizedError


class AuthTokenHandler:
    def __init__(self, secret: str, algorithm: str = "HS256", ttl_seconds: int = 3600) -> None:
        if not secret:
            raise ValueError("AUTH_KEY não configurada.")
        self._secret = secret
        self._algorithm = algorithm
        self._ttl = ttl_seconds

    def encode_token(self, subject: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(seconds=self._ttl),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"require": ["sub", "exp"]},
            )
        except ExpiredSignatureError as exc:
            raise UnauthorizedError("Token expirado.", code="TOKEN_EXPIRED") from exc
        except InvalidTokenError as exc:
            raise UnauthorizedError("Token inválido.", code="INVALID_TOKEN") from exc
