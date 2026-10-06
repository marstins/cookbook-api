from app.application.dto.auth import LoginDTO, LoginResultDTO
from app.application.mappers.user_mapper import UserPublicMapper
from app.domain.exceptions import UnauthorizedError


class AuthService:
    def __init__(
        self,
        user_repository,
        password_hasher,
        user_public_mapper: UserPublicMapper,
        auth_token_handler,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._user_public_mapper = user_public_mapper
        self._auth_token_handler = auth_token_handler

    def login(self, data: LoginDTO) -> LoginResultDTO:
        user = self._user_repository.get_by_email(str(data.email))
        if user is None:
            raise UnauthorizedError(
                "Credenciais inválidas",
                code="INVALID_CREDENTIALS",
            )

        if not self._password_hasher.verify_password(
            data.password, user.password_hash
        ):
            raise UnauthorizedError(
                "Credenciais inválidas",
                code="INVALID_CREDENTIALS",
            )

        public_user = self._user_public_mapper.map_to_public(user)
        return LoginResultDTO(
            user=public_user,
            token=self._auth_token_handler.encode_token(public_user.id),
        )
