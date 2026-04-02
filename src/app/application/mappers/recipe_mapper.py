from app.domain.models.aggregates.recipe.recipe import Recipe, RecipePublic


class RecipePublicMapper:
    def map_to_public(self, recipe: Recipe) -> RecipePublic:
        return RecipePublic(
            title=recipe.title,
            id=recipe.id,
            description=recipe.description,
            instructions=recipe.instructions,
            is_public=recipe.is_public,
            ingredients=recipe.ingredients,
            author_id=recipe.author_id,
            author_name=recipe.author_name,
            original_recipe_id=recipe.original_recipe_id,
            original_author_id=recipe.original_author_id,
            original_author_name=recipe.original_author_name,
            created_at=recipe.created_at,
        )
