from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.application.dto.auth import LoginResultDTO
from app.application.dto.user import (CreateUserDTO, UpdateUserDTO,
                                      UpdateUserPasswordDTO)
from app.application.mappers.user_mapper import UserPublicMapper
from app.domain.exceptions import (ConflictError, NotFoundError,
                                   PersistenceError, UnauthorizedError)
from app.domain.models.aggregates.auth.auth import AuthResponse
from app.domain.models.aggregates.user import UserCreate, UserPublic
from app.domain.models.aggregates.user.user import UserUpdate
from app.infrastructure.persistence.database import db
from app.infrastructure.persistence.repositories import (IngredientRepository,
                                                         RecipeRepository)
from app.infrastructure.security.auth0_client import Auth0Client
from app.infrastructure.security.auth_token_handler import AuthTokenHandler


class UserService:
    def __init__(
        self,
        user_repository,
        password_hasher,
        user_public_mapper: UserPublicMapper,
        recipe_repository: RecipeRepository,
        ingredient_repository: IngredientRepository,
        auth0_client: Auth0Client,
        auth_token_handler: AuthTokenHandler
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._user_public_mapper = user_public_mapper
        self._recipe_repository = recipe_repository
        self._ingredient_repository = ingredient_repository
        self._auth0_client = auth0_client
        self._auth_token_handler = auth_token_handler


    def get_all(self) -> list[UserPublic]:
        users = self._user_repository.get_all()

        if not users:
            return []

        return [self._user_public_mapper.map_to_public(user) for user in users]


    def create(self, data: CreateUserDTO) -> UserPublic:
        existing_user_by_email = self._user_repository.get_by_email(str(data.email))
        if existing_user_by_email:
            raise ConflictError(
                "E-mail fornecido já cadastrado",
                code="EMAIL_ALREADY_REGISTERED",
            )

        existing_user_by_name = self._user_repository.get_by_name(data.name)
        if existing_user_by_name:
            raise ConflictError(
                "Nome fornecido já cadastrado",
                code="NAME_ALREADY_REGISTERED",
            )

        user_to_create = UserCreate(
            name=data.name,
            email=data.email,
        )

        try:
            created_user_in_auth = self._auth0_client.signup(str(data.email), data.password)
        except ConflictError as exc:
            if exc.code != "USER_ALREADY_EXISTS":
                raise
            try:
                self._auth0_client.login(str(data.email), data.password)
            except UnauthorizedError as exc:
                raise ConflictError(
                    "E-mail fornecido já cadastrado",
                    code="EMAIL_ALREADY_REGISTERED",
                ) from exc

            existing_users = self._auth0_client.get_users_by_email(str(data.email).lower())
            if not existing_users or not existing_users[0].user_id:
                raise ConflictError(
                    "E-mail fornecido já cadastrado",
                    code="EMAIL_ALREADY_REGISTERED",
                )

            user_to_create.auth_id = existing_users[0].user_id
        else:
            user_to_create.auth_id = f"auth0|{created_user_in_auth['_id']}"

        try:
            created_user = self._user_repository.create(user_to_create)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(
                "Dados em conflito com o cadastro existente",
                code="UNIQUE_CONSTRAINT_VIOLATION",
            ) from None

        return self._user_public_mapper.map_to_public(created_user)


    def get_by_id(self, user_id: str) -> UserPublic:
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(
                "Usuário não encontrado",
                code="USER_NOT_FOUND",
            )
        return self._user_public_mapper.map_to_public(user)


    def update_password(self, auth_id: str, user_id: str, data: UpdateUserPasswordDTO) -> AuthResponse:
        if data.new_password == data.old_password:
            raise ConflictError(
                "A nova senha não pode ser igual a senha antiga",
                code="IDENTICAL_PASSWORDS_REGISTERED",
            )

        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(
                "Usuário não encontrado",
                code="USER_NOT_FOUND",
            )

        if str(data.email) != user.email:
            raise NotFoundError(
                "Usuário não encontrado",
                code="USER_NOT_FOUND",
            )

        token_credentials = self._auth0_client.change_password(auth_id, data.email, data.old_password, data.new_password)
        decoded_id_token = self._auth_token_handler.decode_id_token(token_credentials["id_token"])

        user_public = self._user_public_mapper.map_to_public(user)
        return AuthResponse(
            user=user_public,
            access_token=token_credentials["access_token"],
            refresh_token=token_credentials["refresh_token"],
            expires_at=decoded_id_token["exp"],
        )


    def update(self, user_id: str, data: UpdateUserDTO) -> UserPublic:
        existing_name_user = self._user_repository.get_by_name(data.name)
        if existing_name_user is not None and existing_name_user.id != user_id:
            raise ConflictError(
                "Nome fornecido já cadastrado",
                code="NAME_ALREADY_REGISTERED",
            )

        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(
                "Usuário não encontrado",
                code="USER_NOT_FOUND",
            )

        if data.name == user.name:
            raise ConflictError(
                "Novo nome não pode ser igual ao antigo",
                code="IDENTICAL_NAME",
            )

        update_data = UserUpdate(**data.model_dump())

        try:
            updated_user = self._user_repository.update(user_id, update_data)
            if updated_user is None:
                raise NotFoundError(
                    "Usuário não encontrado",
                    code="USER_NOT_FOUND",
                )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(
                "Dados em conflito com o cadastro existente",
                code="UNIQUE_CONSTRAINT_VIOLATION",
            ) from None

        return self._user_public_mapper.map_to_public(updated_user)


    def delete(self, user_id: str) -> None:
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(
                "Usuário não encontrado",
                code="USER_NOT_FOUND",
            )
        try:
            recipe_ids = self._recipe_repository.get_recipe_ids_by_author(user_id)
            for recipe_id in recipe_ids:
                self._ingredient_repository.delete_by_recipe_id(recipe_id)
                self._recipe_repository.nullify_original_recipe(recipe_id)
            self._recipe_repository.delete_all_by_author_id(user_id)
            self._recipe_repository.nullify_original_author(user_id)
            self._user_repository.delete(user_id)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(
                "Dados em conflito com o cadastro existente",
                code="UNIQUE_CONSTRAINT_VIOLATION",
            ) from None
        except SQLAlchemyError:
            db.session.rollback()
            raise PersistenceError(
                "Falha ao persistir a exclusão do usuário.",
                code="USER_DELETE_PERSISTENCE_ERROR",
            ) from None
