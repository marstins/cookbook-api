from app.domain.models.aggregates.recipe.recipe import Recipe
from app.infrastructure.persistence.models.recipe_orm import RecipeORM


class RecipeMapper:
    def map_from_orm(self, recipe_orm: RecipeORM) -> Recipe:
        author_name = (
            recipe_orm.author.name
            if recipe_orm.author is not None
            else None
        )
        original_author_name = (
            recipe_orm.original_author.name
            if recipe_orm.original_author is not None
            else None
        )
        data = {
            "id": recipe_orm.id,
            "title": recipe_orm.title,
            "description": recipe_orm.description,
            "instructions": recipe_orm.instructions,
            "is_public": recipe_orm.is_public,
            "ingredients": [
                {
                    "id": ingredient.id,
                    "description": ingredient.description,
                    "recipe_id": ingredient.recipe_id,
                    "created_at": ingredient.created_at,
                }
                for ingredient in recipe_orm.ingredients
            ],
            "author_id": recipe_orm.author_id,
            "author_name": author_name,
            "original_recipe_id": recipe_orm.original_recipe_id,
            "original_author_id": recipe_orm.original_author_id,
            "original_author_name": original_author_name,
            "created_at": recipe_orm.created_at,
        }
        return Recipe.model_validate(data)
