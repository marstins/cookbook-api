from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


_DATA_URI = (
    r"^data:(image/jpeg|image/png|application/pdf);base64,"
    r"[A-Za-z0-9+/]+=*$"
)

class CreateDraftSchema(BaseModel):
    model_config = ConfigDict(title='CreateDraftSchema')

    source_data: str = Field(min_length=1, pattern=_DATA_URI, title='Arquivo com Receita')


class DraftIngredientSchema(BaseModel):
    model_config = ConfigDict(title='DraftIngredientSchema')

    description: str = Field(min_length=1, title='Descrição do ingrediente')


class UpdateDraftSchema(BaseModel):
    model_config = ConfigDict(title='UpdateDraftSchema')

    # 255 é o tamanho das colunas em drafts, não o limite de receita.
    title: str | None = Field(default=None, max_length=255, title='Título da receita')
    description: str | None = Field(default=None, max_length=255, title='Descrição da receita')
    ingredients: list[DraftIngredientSchema] = Field(title='Lista de ingredientes')
    instructions: str | None = Field(default=None, title='Instruções da receita')
