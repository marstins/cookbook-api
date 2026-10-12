import json

from app.domain.models.aggregates.draft.draft import Draft, DraftPublic


class DraftPublicMapper:
    def map_to_public(self, draft: Draft) -> DraftPublic:
        tags_list = json.loads(draft.tags)

        return DraftPublic(
            id=draft.id,
            author_id=draft.author_id,
            title=draft.title,
            description=draft.description,
            instructions=draft.instructions,
            ingredients=json.loads(draft.ingredients) if draft.ingredients else draft.ingredients,
            is_draft=True,
            is_vegetarian='vegetarian' in tags_list,
            is_vegan='vegan' in tags_list,
            is_gluten_free='gluten_free' in tags_list,
            is_lactose_free='lactose_free' in tags_list,
            created_at=draft.created_at,
        )
