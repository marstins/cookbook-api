from pydantic import BaseModel

from .ingredient import CreateIngredientDTO, UpdateIngredientDTO


class CreateRecipeDTO(BaseModel):
    title: str
    description: str
    instructions: str
    is_public: bool
    ingredients: list[CreateIngredientDTO]
    tags: list[str]
    user_id: str


class UpdateRecipeDTO(BaseModel):
    title: str
    description: str
    instructions: str
    ingredients: list[UpdateIngredientDTO]
    is_public: bool
    tags: list[str]


class SaveRecipeDTO(BaseModel):
    recipe_id: str
    user_id: str


class RecipeFilterDTO(BaseModel):
    title: str | None = None
    description: str | None = None
    instructions: str | None = None
    tags: list[str] = []
    author_id: list[str] = []
    get_public: bool | None = None
    exclude_author_id: list[str] = []