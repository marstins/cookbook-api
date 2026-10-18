from datetime import datetime

from pydantic import BaseModel

from .ingredient import Ingredient


class RecipeBase(BaseModel):
    title: str
    description: str
    instructions: str
    is_public: bool


class RecipeCreate(RecipeBase):
    tags: str
    author_id: str
    original_author_id: str | None = None
    original_recipe_id: str | None = None


class RecipeUpdate(RecipeBase):
    tags: str


class RecipePublic(RecipeBase):
    id: str
    ingredients: list[Ingredient]
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool
    is_lactose_free: bool
    author_id: str
    author_name: str
    original_recipe_id: str | None = None
    original_author_id: str | None = None
    original_author_name: str | None = None
    created_at: datetime


class Recipe(RecipeBase):
    id: str
    ingredients: list[Ingredient]
    tags: str
    author_id: str
    author_name: str
    original_recipe_id: str | None = None
    original_author_id: str | None = None
    original_author_name: str | None = None
    created_at: datetime


class RecipeFilter(BaseModel):
    title: str | None = None
    description: str | None = None
    instructions: str | None = None
    tags: list[str] = []
    author_id: list[str] = []
    get_public: bool | None = None
    exclude_author_id: list[str] = []