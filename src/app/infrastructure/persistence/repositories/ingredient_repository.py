from sqlalchemy import select

from app.domain.models.aggregates.recipe.ingredient import (Ingredient,
                                                            IngredientCreate)
from app.infrastructure.persistence.database import db
from app.infrastructure.persistence.models.ingredient_orm import IngredientORM


class IngredientRepository:
    def create(self, data: IngredientCreate) -> Ingredient:
        ingredient = IngredientORM(**data.model_dump())
        db.session.add(ingredient)
        db.session.flush()
        db.session.refresh(ingredient)
        return Ingredient.model_validate(ingredient, from_attributes=True)


    def delete_by_recipe_id(self, recipe_id: str) -> bool:
        ingredients = db.session.scalars(
            select(IngredientORM).where(IngredientORM.recipe_id == recipe_id)
        ).all()
        if not ingredients:
            return False
        for ingredient in ingredients:
            db.session.delete(ingredient)
        db.session.flush()
        return True
