from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.models.aggregates.recipe.recipe import RecipePublic
from app.domain.models.aggregates.draft.draft import DraftPublic


class PaginationMetaDTO(BaseModel):
    page: int
    per_page: int
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class PaginatedRecipesDTO(BaseModel):
    items: list[RecipePublic]
    pagination: PaginationMetaDTO


class PaginatedDraftsDTO(BaseModel):
    items: list[DraftPublic]
    pagination: PaginationMetaDTO


def build_pagination_meta(page: int, per_page: int, total_items: int) -> PaginationMetaDTO:
    if per_page <= 0:
        total_pages = 0
    elif total_items == 0:
        total_pages = 0
    else:
        total_pages = (total_items + per_page - 1) // per_page
    return PaginationMetaDTO(
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
    )
