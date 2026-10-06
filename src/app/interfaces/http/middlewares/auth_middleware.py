from flask import g, request

from app.domain.exceptions import UnauthorizedError
from app.infrastructure.security import AuthTokenHandler


class AuthMiddleware:
    def __init__(self, auth_token_handler: AuthTokenHandler) -> None:
        self._auth_token_handler = auth_token_handler

    def validate(self) -> None:
        if request.method == "OPTIONS":
            return
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise UnauthorizedError("Token não encontrado.", code="TOKEN_NOT_FOUND")
        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            raise UnauthorizedError("Token não encontrado.", code="TOKEN_NOT_FOUND")
        decoded = self._auth_token_handler.decode_token(token)
        g.user_id = decoded["sub"]

    def validate_users(self) -> None:
        if request.endpoint == "users_bp.create_user":
            return
        self.validate()
        path_user_id = (request.view_args or {}).get("user_id")
        if path_user_id is not None and path_user_id != g.user_id:
            raise UnauthorizedError(
                "O token não corresponde a este usuário.",
                code="USER_MISMATCH",
            )
