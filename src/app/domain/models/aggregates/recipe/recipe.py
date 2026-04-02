from datetime import datetime

from pydantic import BaseModel

from .ingredient import Ingredient


class RecipeBase(BaseModel):
    title: str
    description: str
    instructions: str
    is_public: bool


class RecipeCreate(RecipeBase):
    author_id: str
    original_author_id: str | None = None
    original_recipe_id: str | None = None


class RecipeUpdate(RecipeBase):
    pass


class RecipePublic(RecipeBase):
    id: str
    ingredients: list[Ingredient]
    author_id: str
    author_name: str
    original_recipe_id: str | None = None
    original_author_id: str | None = None
    original_author_name: str | None = None
    created_at: datetime


class Recipe(RecipeBase):
    id: str
    ingredients: list[Ingredient]
    author_id: str
    author_name: str
    original_recipe_id: str | None = None
    original_author_id: str | None = None
    original_author_name: str | None = None
    created_at: datetime
