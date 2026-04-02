from pydantic import BaseModel

from .ingredient import CreateIngredientDTO, UpdateIngredientDTO


class CreateRecipeDTO(BaseModel):
    title: str
    description: str
    instructions: str
    is_public: bool
    ingredients: list[CreateIngredientDTO]
    user_id: str


class UpdateRecipeDTO(BaseModel):
    title: str
    description: str
    instructions: str
    ingredients: list[UpdateIngredientDTO]
    is_public: bool


class SaveRecipeDTO(BaseModel):
    recipe_id: str
    user_id: str
