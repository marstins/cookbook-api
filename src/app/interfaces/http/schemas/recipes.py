from typing import Literal

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


RecipeTag = Literal["vegan", "vegetarian", "gluten_free", "lactose_free"]


class CreateIngredientSchema(BaseModel):
    model_config = ConfigDict(title='CreateIngredientSchema')

    description: str = Field(min_length=1, max_length=30, title='Descrição do ingrediente')


class CreateRecipeSchema(BaseModel):
    model_config = ConfigDict(title='CreateRecipeSchema')

    title: str = Field(min_length=1, max_length=40, title='Título da receita')
    description: str = Field(min_length=1, max_length=50, title='Descrição da receita')
    ingredients: list[CreateIngredientSchema] = Field(min_length=1, title='Lista de ingredientes')
    instructions: str = Field(min_length=1, max_length=1000, title='Instruções da receita')
    is_public: bool = Field(default=False, title='Status público da receita')
    tags: list[RecipeTag] = Field(title='Tags da receita')


class SaveRecipeSchema(BaseModel):
    model_config = ConfigDict(title='SaveRecipeSchema')

    recipe_id: str = Field(max_length=36, title='Id da receita a ser salva')


class UpdateIngredientSchema(BaseModel):
    model_config = ConfigDict(title='UpdateIngredientSchema')

    description: str = Field(min_length=1, max_length=30, title='Descrição do ingrediente')


class UpdateRecipeSchema(BaseModel):
    model_config = ConfigDict(title='UpdateRecipeSchema')

    title: str = Field(min_length=1, max_length=40, title='Título da receita')
    description: str = Field(min_length=1, max_length=50, title='Descrição da receita')
    ingredients: list[UpdateIngredientSchema] = Field(min_length=1, title='Lista de ingredientes')
    instructions: str = Field(min_length=1, max_length=1000, title='Instruções da receita')
    is_public: bool = Field(default=False, title='Status público da receita')
    tags: list[RecipeTag] = Field(title='Tags da receita')

class RecipeFilterSchema(BaseModel):
    model_config = ConfigDict(title='RecipeFilters')

    title: str  | None = Field(default=None, min_length=1, max_length=40, title='Título da receita')
    description: str | None = Field(default=None, min_length=1, max_length=50, title='Descrição da receita')
    instructions: str = Field(default=None, min_length=1, max_length=1000, title='Instruções da receita')
    tags: list[RecipeTag] = Field(default_factory=list, title='Tags da receita')
    author_id: list[str] = Field(default_factory=list, title='Id do autor da receita')
