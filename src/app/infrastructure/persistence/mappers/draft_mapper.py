from app.domain.models.aggregates.draft.draft import Draft
from app.infrastructure.persistence.models.draft_orm import DraftORM


class DraftMapper:
    def map_from_orm(self, draft_orm: DraftORM) -> Draft:
        data = {
            "id": draft_orm.id,
            "title": draft_orm.title,
            "description": draft_orm.description,
            "instructions": draft_orm.instructions,
            "ingredients": draft_orm.ingredients,
            "author_id": draft_orm.author_id,
            "created_at": draft_orm.created_at,
        }
        return Draft.model_validate(data)
