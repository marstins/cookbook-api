from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.application.dto.user import (CreateUserDTO, UpdateUserNameDTO,
                                      UpdateUserPasswordDTO)
from app.application.mappers.user_mapper import UserPublicMapper
from app.domain.exceptions import (ConflictError, NotFoundError,
                                   PersistenceError)
from app.domain.models.aggregates.user import UserCreate, UserPublic
from app.infrastructure.persistence.database import db
from app.infrastructure.persistence.repositories import (IngredientRepository,
                                                         RecipeRepository)


class UserService:
    def __init__(
        self,
        user_repository,
        password_hasher,
        user_public_mapper: UserPublicMapper,
        recipe_repository: RecipeRepository,
        ingredient_repository: IngredientRepository,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._user_public_mapper = user_public_mapper
        self._recipe_repository = recipe_repository
        self._ingredient_repository = ingredient_repository


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

        password_hash = self._password_hasher.hash_password(data.password)
        user_to_create = UserCreate(
            name=data.name,
            email=data.email,
            password_hash=password_hash,
        )

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


    def update_password(self, user_id: str, data: UpdateUserPasswordDTO) -> UserPublic:
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

        if not self._password_hasher.verify_password(
            data.old_password, user.password_hash
        ):
            raise ConflictError(
                "Senha atual incorreta",
                code="INVALID_PASSWORD",
            )

        new_hash = self._password_hasher.hash_password(data.new_password)
        try:
            updated_user = self._user_repository.update_password(user_id, new_hash)
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


    def update_name(self, user_id: str, data: UpdateUserNameDTO) -> UserPublic:
        existing_name_user = self._user_repository.get_by_name(data.new_name)
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

        if str(data.email) != user.email:
            raise NotFoundError(
                "Usuário não encontrado",
                code="USER_NOT_FOUND",
            )

        if data.new_name == user.name:
            raise ConflictError(
                "Novo nome não pode ser igual ao antigo",
                code="IDENTICAL_NAME",
            )

        try:
            updated_user = self._user_repository.update_name(user_id, data.new_name)
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
