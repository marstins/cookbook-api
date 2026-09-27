from datetime import datetime

from pydantic import BaseModel


class DraftBase(BaseModel):
    instructions: str


class DraftIngredient(BaseModel):
    description: str


class DraftCreate(DraftBase):
    author_id: str
    ingredients: str
    title: str | None = None
    description: str | None = None
    instructions: str | None = None


class DraftUpdate(DraftBase):
    description: str | None = None
    ingredients: str
    title: str | None = None
    instructions: str | None = None


class DraftPublic(DraftBase):
    id: str
    author_id: str
    title: str | None = None
    ingredients: list[DraftIngredient]
    description: str | None = None
    instructions: str | None = None
    is_draft: bool
    created_at: datetime


class Draft(DraftBase):
    id: str
    author_id: str
    ingredients: str
    title: str | None = None
    description: str | None = None
    instructions: str | None = None
    created_at: datetime
