from flask import g, request

from app.domain.exceptions import UnauthorizedError
from app.infrastructure.security import AuthTokenHandler
from app.services.auth_service import AuthService


class AuthMiddleware:
    def __init__(self, auth_token_handler: AuthTokenHandler, auth_service: AuthService) -> None:
        self._auth_token_handler = auth_token_handler
        self._auth_service = auth_service

    def validate(self) -> None:
        if request.method == "OPTIONS":
            return
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise UnauthorizedError("Token não encontrado.", code="TOKEN_NOT_FOUND")
        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            raise UnauthorizedError("Token não encontrado.", code="TOKEN_NOT_FOUND")
        decoded = self._auth_token_handler.decode(token)
        user = self._auth_service.resolve_current_user(decoded["sub"])
        g.auth_id = decoded["sub"]
        g.user_id = user.id

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
