from app.application.dto.auth import LoginDTO, LoginResultDTO, RefreshTokenDTO
from app.application.mappers.user_mapper import UserPublicMapper
from app.domain.exceptions import UnauthorizedError
from app.domain.models.aggregates.auth.auth import AuthResponse
from app.domain.models.aggregates.user.user import User
from app.infrastructure.persistence.repositories.user_repository import UserRepository
from app.infrastructure.security.auth0_client import Auth0Client
from app.infrastructure.security.auth_token_handler import AuthTokenHandler


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_public_mapper: UserPublicMapper,
        auth0_client: Auth0Client,
        auth_token_handler: AuthTokenHandler,
    ) -> None:
        self._user_repository = user_repository
        self._user_public_mapper = user_public_mapper
        self._auth0_client = auth0_client
        self._auth_token_handler = auth_token_handler

    def login(self, data: LoginDTO) -> AuthResponse:
        token_credentials = self._auth0_client.login(data.email, data.password)
        decoded_id_token = self._auth_token_handler.decode_id_token(token_credentials["id_token"])

        user = self._user_repository.get_by_auth_id(decoded_id_token["sub"])
        if user is None:
            raise UnauthorizedError(
                "Credenciais inválidas",
                code="INVALID_CREDENTIALS",
            )

        public_user = self._user_public_mapper.map_to_public(user)
        return AuthResponse(
            user=public_user,
            access_token=token_credentials["access_token"],
            refresh_token=token_credentials["refresh_token"],
            expires_at=decoded_id_token["exp"],
        )

    def refresh_token(self, data: RefreshTokenDTO) -> AuthResponse:
        token_credentials = self._auth0_client.refresh_token(data.refresh_token)
        decoded_id_token = self._auth_token_handler.decode_id_token(token_credentials["id_token"])

        user = self._user_repository.get_by_auth_id(decoded_id_token["sub"])
        if user is None:
            raise UnauthorizedError(
                "Credenciais inválidas",
                code="INVALID_CREDENTIALS",
            )

        public_user = self._user_public_mapper.map_to_public(user)
        return AuthResponse(
            user=public_user,
            access_token=token_credentials["access_token"],
            refresh_token=token_credentials["refresh_token"],
            expires_at=decoded_id_token["exp"],
        )

    def resolve_current_user(self, auth_id: str) -> User:
        user = self._user_repository.get_by_auth_id(auth_id)
        if user is None:
            raise UnauthorizedError(
                "Usuário não encontrado.",
                code="USER_NOT_FOUND",
            )
        return user
