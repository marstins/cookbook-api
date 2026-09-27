from sqlalchemy import select, update
from sqlalchemy.sql.functions import count

from app.domain.models.aggregates.draft.draft import (Draft, DraftCreate, DraftUpdate)
from app.infrastructure.persistence.database import db
from app.infrastructure.persistence.mappers.draft_mapper import DraftMapper
from app.infrastructure.persistence.models.draft_orm import DraftORM


class DraftRepository:
    def __init__(self, draft_mapper: DraftMapper) -> None:
        self._draft_mapper = draft_mapper

    # Fazer
    def create(self, data: DraftCreate) -> Draft:
        draft = DraftORM(**data.model_dump())
        db.session.add(draft)
        db.session.flush()
        db.session.refresh(draft)
        return self._draft_mapper.map_from_orm(draft)

    def get_all(self) -> list[Draft]:
        drafts = db.session.scalars(
            select(DraftORM)
            .order_by(DraftORM.created_at)
        ).all()
        return [self._draft_mapper.map_from_orm(draft) for draft in drafts]

    def count_public(self, exclude_author_id: str | None = None) -> int:
        stmt = (
            select(count())
            .select_from(DraftORM)
            .where(DraftORM.is_public.is_(True))
        )
        if exclude_author_id is not None:
            stmt = stmt.where(DraftORM.author_id != exclude_author_id)
        return int(db.session.scalar(stmt) or 0)

    def count_by_author_id(self, author_id: str) -> int:
        total = db.session.scalar(
            select(count())
            .select_from(DraftORM)
            .where(DraftORM.author_id == author_id)
        )
        return int(total or 0)

    #Fazer
    def update(self, draft_id: str, data: DraftUpdate) -> Draft | None:
        draft_orm = db.session.scalar(
            select(DraftORM)
            .where(DraftORM.id == draft_id)
        )
        if draft_orm is None:
            return None
        draft_orm.title = data.title
        draft_orm.description = data.description
        draft_orm.instructions = data.instructions
        draft_orm.ingredients = data.ingredients
        db.session.flush()
        db.session.refresh(draft_orm)
        return self._draft_mapper.map_from_orm(draft_orm)

    def delete(self, draft_id: str) -> bool:
        draft = db.session.scalar(
            select(DraftORM).where(DraftORM.id == draft_id)
        )
        if draft is None:
            return False
        db.session.delete(draft)
        db.session.flush()
        return True

    def get_all_by_author_id(self, author_id: str, offset: int, per_page: int) -> list[Draft]:
        drafts = db.session.scalars(
            select(DraftORM)
            .where(DraftORM.author_id == author_id)
            .order_by(DraftORM.created_at)
            .offset(offset)
            .limit(per_page)
        ).all()
        return [self._draft_mapper.map_from_orm(draft) for draft in drafts]

    def delete_all_by_author_id(self, author_id: str) -> None:
        drafts = db.session.scalars(
            select(DraftORM).where(DraftORM.author_id == author_id)
        ).all()
        for draft in drafts:
            db.session.delete(draft)
        db.session.flush()

    def get_by_id(self, draft_id: str) -> Draft | None:
        draft_orm = db.session.scalar(
            select(DraftORM)
            .where(DraftORM.id == draft_id)
        )
        if draft_orm is None:
            return None
        return self._draft_mapper.map_from_orm(draft_orm)
