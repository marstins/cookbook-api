from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from app.core.config import Config
from app.domain.models.aggregates.recipe.recipe import RecipePublic


class PaginationSchema(BaseModel):
    model_config = ConfigDict(title="PaginationSchema")

    page: int = Field(gt=0, default=1, title="Página")
    per_page: int = Field(
        gt=0,
        default=Config.PAGINATION_DEFAULT_PER_PAGE,
        le=Config.PAGINATION_MAX_PER_PAGE,
        title="Registros por página",
    )


class PaginationResponseSchema(BaseModel):
    model_config = ConfigDict(title="PaginationResponseSchema")

    page: int = Field(title="Página atual")
    per_page: int = Field(title="Registros por página")
    total_items: int = Field(ge=0, title="Total de registros que atendem ao filtro")
    total_pages: int = Field(ge=0, title="Total de páginas")


class PaginatedRecipeListResponseSchema(BaseModel):
    model_config = ConfigDict(title="PaginatedRecipeListResponseSchema")

    items: list[RecipePublic] = Field(title="Receitas da página")
    pagination: PaginationResponseSchema = Field(title="Metadados de paginação")
