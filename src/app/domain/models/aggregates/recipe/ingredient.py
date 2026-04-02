from datetime import datetime

from pydantic import BaseModel


class IngredientBase(BaseModel):
    description: str


class IngredientCreate(IngredientBase):
    recipe_id: str


class Ingredient(IngredientBase):
    id: str
    recipe_id: str
    created_at: datetime
