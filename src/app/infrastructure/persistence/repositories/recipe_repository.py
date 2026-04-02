from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.functions import count

from app.domain.models.aggregates.recipe.recipe import (Recipe, RecipeCreate,
                                                        RecipeUpdate)
from app.infrastructure.persistence.database import db
from app.infrastructure.persistence.mappers.recipe_mapper import RecipeMapper
from app.infrastructure.persistence.models.recipe_orm import RecipeORM


class RecipeRepository:
    def __init__(self, recipe_mapper: RecipeMapper) -> None:
        self._recipe_mapper = recipe_mapper

    def create(self, data: RecipeCreate) -> Recipe:
        recipe = RecipeORM(**data.model_dump())
        db.session.add(recipe)
        db.session.flush()
        db.session.refresh(recipe)
        return self._recipe_mapper.map_from_orm(recipe)

    def get_all(self) -> list[Recipe]:
        recipes = db.session.scalars(
            select(RecipeORM)
            .options(
                selectinload(RecipeORM.ingredients),
                joinedload(RecipeORM.author),
                joinedload(RecipeORM.original_author),
            )
            .order_by(RecipeORM.created_at)
        ).all()
        return [self._recipe_mapper.map_from_orm(recipe) for recipe in recipes]

    def get_all_public(
        self,
        offset: int,
        per_page: int,
        exclude_author_id: str | None = None,
    ) -> list[Recipe]:
        stmt = (
            select(RecipeORM)
            .where(RecipeORM.is_public.is_(True))
            .options(
                selectinload(RecipeORM.ingredients),
                joinedload(RecipeORM.author),
                joinedload(RecipeORM.original_author),
            )
            .order_by(RecipeORM.created_at)
        )
        if exclude_author_id is not None:
            stmt = stmt.where(RecipeORM.author_id != exclude_author_id)
        recipes = db.session.scalars(
            stmt.offset(offset).limit(per_page)
        ).all()
        return [self._recipe_mapper.map_from_orm(recipe) for recipe in recipes]

    def count_public(self, exclude_author_id: str | None = None) -> int:
        stmt = (
            select(count())
            .select_from(RecipeORM)
            .where(RecipeORM.is_public.is_(True))
        )
        if exclude_author_id is not None:
            stmt = stmt.where(RecipeORM.author_id != exclude_author_id)
        return int(db.session.scalar(stmt) or 0)

    def count_by_author_id(self, author_id: str) -> int:
        total = db.session.scalar(
            select(count())
            .select_from(RecipeORM)
            .where(RecipeORM.author_id == author_id)
        )
        return int(total or 0)

    def update(self, recipe_id: str, data: RecipeUpdate) -> Recipe | None:
        recipe_orm = db.session.scalar(
            select(RecipeORM)
            .where(RecipeORM.id == recipe_id)
            .options(
                selectinload(RecipeORM.ingredients),
                joinedload(RecipeORM.author),
                joinedload(RecipeORM.original_author),
            )
        )
        if recipe_orm is None:
            return None
        recipe_orm.title = data.title
        recipe_orm.description = data.description
        recipe_orm.instructions = data.instructions
        recipe_orm.is_public = data.is_public
        db.session.flush()
        db.session.refresh(recipe_orm)
        return self._recipe_mapper.map_from_orm(recipe_orm)

    def delete(self, recipe_id: str) -> bool:
        recipe = db.session.scalar(
            select(RecipeORM).where(RecipeORM.id == recipe_id)
        )
        if recipe is None:
            return False
        db.session.delete(recipe)
        db.session.flush()
        return True

    def get_all_by_author_id(self, author_id: str, offset: int, per_page: int) -> list[Recipe]:
        recipes = db.session.scalars(
            select(RecipeORM)
            .where(RecipeORM.author_id == author_id)
            .options(
                selectinload(RecipeORM.ingredients),
                joinedload(RecipeORM.author),
                joinedload(RecipeORM.original_author),
            )
            .order_by(RecipeORM.created_at)
            .offset(offset)
            .limit(per_page)
        ).all()
        return [self._recipe_mapper.map_from_orm(recipe) for recipe in recipes]

    def nullify_original_recipe(self, recipe_id: str) -> None:
        db.session.execute(
            update(RecipeORM)
            .where(RecipeORM.original_recipe_id == recipe_id)
            .values(original_recipe_id=None)
        )
        db.session.flush()

    def nullify_original_author(self, author_id: str) -> None:
        db.session.execute(
            update(RecipeORM)
            .where(RecipeORM.original_author_id == author_id)
            .values(original_author_id=None)
        )
        db.session.flush()

    def get_recipe_ids_by_author(self, author_id: str) -> list[str]:
        recipes = db.session.scalars(
            select(RecipeORM.id).where(RecipeORM.author_id == author_id)
        ).all()
        return list(recipes)

    def delete_all_by_author_id(self, author_id: str) -> None:
        recipes = db.session.scalars(
            select(RecipeORM).where(RecipeORM.author_id == author_id)
        ).all()
        for recipe in recipes:
            db.session.delete(recipe)
        db.session.flush()

    def author_has_fork_of_original(
        self,
        author_id: str,
        original_recipe_id: str,
    ) -> bool:
        recipe_id = db.session.scalar(
            select(RecipeORM.id)
            .where(
                RecipeORM.author_id == author_id,
                RecipeORM.original_recipe_id == original_recipe_id,
            )
            .limit(1)
        )
        return recipe_id is not None

    def get_by_id(self, recipe_id: str) -> Recipe | None:
        recipe_orm = db.session.scalar(
            select(RecipeORM)
            .where(RecipeORM.id == recipe_id)
            .options(
                selectinload(RecipeORM.ingredients),
                joinedload(RecipeORM.author),
                joinedload(RecipeORM.original_author),
            )
        )
        if recipe_orm is None:
            return None
        return self._recipe_mapper.map_from_orm(recipe_orm)
