from pydantic import BaseModel

from .ingredient import UpdateIngredientDTO


class CreateDraftDTO(BaseModel):
    source_data: str
    user_id: str


class UpdateDraftDTO(BaseModel):
    title: str | None = None
    description: str | None = None
    instructions: str | None = None
    ingredients: list[UpdateIngredientDTO]

