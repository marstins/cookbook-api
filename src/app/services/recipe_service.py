from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.application.dto.pagination import (PaginatedRecipesDTO,
                                            build_pagination_meta)
from app.application.dto.recipe import (CreateRecipeDTO, SaveRecipeDTO,
                                        UpdateRecipeDTO)
from app.application.mappers.recipe_mapper import RecipePublicMapper
from app.domain.exceptions import (ConflictError, NotFoundError,
                                   PersistenceError, UnauthorizedError)
from app.domain.models.aggregates.recipe.ingredient import IngredientCreate
from app.domain.models.aggregates.recipe.recipe import (RecipeCreate,
                                                        RecipePublic,
                                                        RecipeUpdate)
from app.infrastructure.persistence.database import db
from app.infrastructure.persistence.repositories import (IngredientRepository,
                                                         UserRepository)


class RecipeService:
    def __init__(
        self,
        recipe_repository,
        recipe_public_mapper: RecipePublicMapper,
        user_repository: UserRepository,
        ingredient_repository: IngredientRepository,
    ) -> None:
        self._recipe_repository = recipe_repository
        self._recipe_public_mapper = recipe_public_mapper
        self._user_repository = user_repository
        self._ingredient_repository = ingredient_repository

    def get_all(self) -> list[RecipePublic]:
        recipes = self._recipe_repository.get_all()
        return [
            self._recipe_public_mapper.map_to_public(recipe) for recipe in recipes
        ]

    def create(self, recipe: CreateRecipeDTO) -> RecipePublic:
        try:
            user = self._user_repository.get_by_id(recipe.user_id)
            if user is None:
                raise NotFoundError(
                    "Usuário não encontrada",
                    code="RECIPE_AUTHOR_NOT_FOUND",
            )
            recipe_to_create = RecipeCreate(
                title=recipe.title,
                description=recipe.description,
                instructions=recipe.instructions,
                is_public=recipe.is_public,
                author_id=recipe.user_id,
            )
            created_recipe = self._recipe_repository.create(recipe_to_create)
            ingredients_to_create = [
                IngredientCreate(
                    description=ingredient.description,
                    recipe_id=created_recipe.id,
                )
                for ingredient in recipe.ingredients
            ]
            for ingredient in ingredients_to_create:
                self._ingredient_repository.create(ingredient)
            recipe = self._recipe_repository.get_by_id(created_recipe.id)
            if recipe is None:
                raise NotFoundError(
                    "Receita não encontrada.",
                    code="RECIPE_NOT_FOUND",
            )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(
                "Não foi possível criar a receita.",
                code="RECIPE_CREATE_INTEGRITY_ERROR",
            ) from None
        except SQLAlchemyError:
            db.session.rollback()
            raise PersistenceError(
                "Falha ao persistir a receita.",
                code="RECIPE_CREATE_PERSISTENCE_ERROR",
            ) from None

        return self._recipe_public_mapper.map_to_public(recipe)

    def get_all_public(
        self,
        user_id: str | None,
        page: int,
        per_page: int,
    ) -> PaginatedRecipesDTO:
        total_items = self._recipe_repository.count_public(
            exclude_author_id=user_id,
        )
        offset = (page - 1) * per_page
        recipes = self._recipe_repository.get_all_public(
            offset,
            per_page,
            exclude_author_id=user_id,
        )
        items = [
            self._recipe_public_mapper.map_to_public(recipe) for recipe in recipes
        ]
        return PaginatedRecipesDTO(
            items=items,
            pagination=build_pagination_meta(page, per_page, total_items),
        )

    def get_by_id(self, recipe_id: str) -> RecipePublic:
        recipe = self._recipe_repository.get_by_id(recipe_id)
        if recipe is None:
            raise NotFoundError(
                "Receita não encontrada.",
                code="RECIPE_NOT_FOUND",
            )
        return self._recipe_public_mapper.map_to_public(recipe)

    def update(self, recipe_id: str, user_id: str, data: UpdateRecipeDTO) -> RecipePublic:
        recipe = self._recipe_repository.get_by_id(recipe_id)
        if recipe is None:
            raise NotFoundError(
                "Receita não encontrada.",
                code="RECIPE_NOT_FOUND",
            )
        if recipe.author_id != user_id:
            raise UnauthorizedError(
                "Você não é o criador dessa receita.",
                code="RECIPE_NOT_OWNED"
            )
        try:
            recipe_to_update = RecipeUpdate(
                title=data.title,
                description=data.description,
                instructions=data.instructions,
                is_public=data.is_public,
            )
            self._ingredient_repository.delete_by_recipe_id(recipe_id)
            ingredients_to_create = [
                IngredientCreate(
                    description=ingredient.description,
                    recipe_id=recipe_id,
                )
                for ingredient in data.ingredients
            ]
            for ingredient in ingredients_to_create:
                self._ingredient_repository.create(ingredient)
            updated_recipe = self._recipe_repository.update(recipe_id, recipe_to_update)
            if updated_recipe is None:
                db.session.rollback()
                raise NotFoundError(
                    "Receita não encontrada.",
                    code="RECIPE_NOT_FOUND_AFTER_UPDATE",
                )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(
                "Não foi possível atualizar a receita.",
                code="RECIPE_UPDATE_INTEGRITY_ERROR",
            ) from None
        except SQLAlchemyError:
            db.session.rollback()
            raise PersistenceError(
                "Falha ao persistir a receita.",
                code="RECIPE_UPDATE_PERSISTENCE_ERROR",
            ) from None

        return self._recipe_public_mapper.map_to_public(updated_recipe)

    def delete(self, recipe_id: str, user_id: str) -> None:
        recipe = self._recipe_repository.get_by_id(recipe_id)
        if recipe is None:
            raise NotFoundError(
                "Receita não encontrada.",
                code="RECIPE_NOT_FOUND",
            )
        if recipe.author_id != user_id:
            raise UnauthorizedError(
                "Você não é o criador dessa receita.",
                code="RECIPE_NOT_OWNED"
            )
        try:
            self._ingredient_repository.delete_by_recipe_id(recipe_id)
            self._recipe_repository.nullify_original_recipe(recipe_id)
            self._recipe_repository.delete(recipe_id)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(
                "Não foi possível excluir a receita devido a restrições de integridade no banco.",
                code="RECIPE_DELETE_INTEGRITY_ERROR",
            ) from None
        except SQLAlchemyError:
            db.session.rollback()
            raise PersistenceError(
                "Falha ao persistir a exclusão da receita.",
                code="RECIPE_DELETE_PERSISTENCE_ERROR",
            ) from None

    def get_all_by_author_id(
        self,
        author_id: str,
        page: int,
        per_page: int,
    ) -> PaginatedRecipesDTO:
        user = self._user_repository.get_by_id(author_id)
        if user is None:
            raise NotFoundError(
                "Usuário não encontrado",
                code="USER_NOT_FOUND",
            )
        total_items = self._recipe_repository.count_by_author_id(author_id)
        offset = (page - 1) * per_page
        recipes = self._recipe_repository.get_all_by_author_id(
            author_id, offset, per_page
        )
        items = [
            self._recipe_public_mapper.map_to_public(recipe) for recipe in recipes
        ]
        return PaginatedRecipesDTO(
            items=items,
            pagination=build_pagination_meta(page, per_page, total_items),
        )

    def save(self, data: SaveRecipeDTO) -> RecipePublic:
        try:
            recipe = self._recipe_repository.get_by_id(data.recipe_id)
            if recipe is None:
                raise NotFoundError(
                    "Receita original não encontrada",
                    code="ORIGINAL_RECIPE_NOT_FOUND",
                )
            user = self._user_repository.get_by_id(data.user_id)
            if user is None:
                raise NotFoundError(
                    "Usuário não encontrado",
                    code="USER_NOT_FOUND",
                )
            if self._recipe_repository.author_has_fork_of_original(
                data.user_id,
                data.recipe_id,
            ):
                raise ConflictError(
                    "Você já salvou essa receita.",
                    code="RECIPE_SAVE_DUPLICATE_FORK",
                )
            recipe_to_save = RecipeCreate(
                title=recipe.title,
                description=recipe.description,
                instructions=recipe.instructions,
                is_public=recipe.is_public,
                author_id=data.user_id,
                original_author_id=recipe.author_id,
                original_recipe_id=data.recipe_id,
            )
            created_recipe = self._recipe_repository.create(recipe_to_save)
            ingredients_to_create = [
                IngredientCreate(
                    description=ingredient.description,
                    recipe_id=created_recipe.id,
                )
                for ingredient in recipe.ingredients
            ]
            for ingredient in ingredients_to_create:
                self._ingredient_repository.create(ingredient)
            saved_recipe = self._recipe_repository.get_by_id(created_recipe.id)
            if saved_recipe is None:
                db.session.rollback()
                raise NotFoundError(
                    "Receita não encontrada.",
                    code="RECIPE_NOT_FOUND_AFTER_SAVE",
                )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(
                "Não foi possível salvar a receita.",
                code="RECIPE_SAVE_INTEGRITY_ERROR",
            ) from None
        except SQLAlchemyError:
            db.session.rollback()
            raise PersistenceError(
                "Falha ao persistir a receita.",
                code="RECIPE_SAVE_PERSISTENCE_ERROR",
            ) from None

        return self._recipe_public_mapper.map_to_public(saved_recipe)
