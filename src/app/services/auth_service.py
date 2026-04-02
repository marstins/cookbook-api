from app.application.dto.auth import LoginDTO
from app.application.mappers.user_mapper import UserPublicMapper
from app.domain.exceptions import UnauthorizedError
from app.domain.models.aggregates.user import UserPublic


class AuthService:
    def __init__(
        self,
        user_repository,
        password_hasher,
        user_public_mapper: UserPublicMapper,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._user_public_mapper = user_public_mapper

    def login(self, data: LoginDTO) -> UserPublic:
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

        return self._user_public_mapper.map_to_public(user)
