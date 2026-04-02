from pydantic import BaseModel


class CreateIngredientDTO(BaseModel):
    description: str


class UpdateIngredientDTO(BaseModel):
    description: str
