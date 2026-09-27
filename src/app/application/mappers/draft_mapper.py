import json

from app.domain.models.aggregates.draft.draft import Draft, DraftPublic


class DraftPublicMapper:
    def map_to_public(self, draft: Draft) -> DraftPublic:
        return DraftPublic(
            id=draft.id,
            author_id=draft.author_id,
            title=draft.title,
            description=draft.description,
            instructions=draft.instructions,
            ingredients=json.loads(draft.ingredients) if draft.ingredients else draft.ingredients,
            is_draft=True,
            created_at=draft.created_at,
        )
