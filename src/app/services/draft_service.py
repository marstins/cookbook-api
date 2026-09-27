import json

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.application.dto.pagination import (PaginatedDraftsDTO,
                                            build_pagination_meta)
from app.application.dto.draft import (CreateDraftDTO, UpdateDraftDTO)
from app.application.mappers.draft_mapper import DraftPublicMapper
from app.domain.exceptions import (ConflictError, NotFoundError,
                                   PersistenceError, UnauthorizedError)
from app.domain.models.aggregates.draft.draft import (DraftCreate,
                                                        Draft,
                                                        DraftUpdate)
from app.infrastructure.persistence.repositories import (UserRepository)
from app.infrastructure.persistence.database import db
from app.services.decode_draft_image_service import DecodeDraftImageService


class DraftService:
    def __init__(
        self,
        draft_repository,
        draft_public_mapper: DraftPublicMapper,
        user_repository: UserRepository,
        decode_draft_image_service: DecodeDraftImageService,
    ) -> None:
        self._draft_repository = draft_repository
        self._draft_public_mapper = draft_public_mapper
        self._user_repository = user_repository
        self._decode_draft_image_service = decode_draft_image_service

    def get_all(self) -> list[Draft]:
        drafts = self._draft_repository.get_all()
        return [
            self._draft_public_mapper.map_to_public(draft) for draft in drafts
        ]

    def create(self, draft: CreateDraftDTO) -> Draft:
        try:
            user = self._user_repository.get_by_id(draft.user_id)
            if user is None:
                raise NotFoundError(
                    "Usuário não encontrado.",
                    code="DRAFT_AUTHOR_NOT_FOUND",
                )

            draft_text = self._decode_draft_image_service.decode_draft_image(
                draft.source_data
            )
            normalized = draft_text.lower()
            ingredients_at = normalized.find("ingredientes")
            instructions_at = normalized.find("modo de preparo")
            has_title_section = ingredients_at > 0
            has_ingredients_section = ingredients_at >= 0
            has_instructions_section = instructions_at >= 0

            draft_title = (
                draft_text[:ingredients_at].strip() if has_title_section else None
            )

            if (
                has_ingredients_section
                and has_instructions_section
                and instructions_at > ingredients_at
            ):
                fatia = draft_text[ingredients_at:instructions_at]
                filtered_ingredients = [
                    linha.strip().lstrip("-* ")
                    for linha in fatia.splitlines()
                    if linha.strip() and "ingredientes" not in linha.lower()
                ]
                after_header = draft_text[instructions_at:]
                first_break = after_header.find("\n")
                draft_instructions = (
                    after_header[first_break + 1:].strip()
                    if first_break >= 0
                    else None
                )
            else:
                filtered_ingredients = []
                draft_instructions = None

            draft_to_create = DraftCreate(
                title=draft_title,
                description=None,
                ingredients=json.dumps(
                    [{"description": linha} for linha in filtered_ingredients]
                ),
                instructions=draft_instructions or draft_text,
                author_id=draft.user_id,
            )
            created_draft = self._draft_repository.create(draft_to_create)
            draft = self._draft_repository.get_by_id(created_draft.id)
            if draft is None:
                raise NotFoundError(
                    "Rascunho não encontrado.",
                    code="DRAFT_NOT_FOUND",
                )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(
                "Não foi possível criar o rascunho.",
                code="DRAFT_CREATE_INTEGRITY_ERROR",
            ) from None
        except SQLAlchemyError:
            db.session.rollback()
            raise PersistenceError(
                "Falha ao persistir o rascunho.",
                code="DRAFT_CREATE_PERSISTENCE_ERROR",
            ) from None

        return self._draft_public_mapper.map_to_public(draft)

    def get_by_id(self, draft_id: str) -> Draft:
        draft = self._draft_repository.get_by_id(draft_id)
        if draft is None:
            raise NotFoundError(
                "Rascunho não encontrado.",
                code="DRAFT_NOT_FOUND",
            )
        return self._draft_public_mapper.map_to_public(draft)

    def update(self, draft_id: str, user_id: str, data: UpdateDraftDTO) -> Draft:
        draft = self._draft_repository.get_by_id(draft_id)
        if draft is None:
            raise NotFoundError(
                "Rascunho não encontrado.",
                code="DRAFT_NOT_FOUND",
            )
        if draft.author_id != user_id:
            raise UnauthorizedError(
                "Você não é o criador desse rascunho.",
                code="DRAFT_NOT_OWNED",
            )
        try:
            draft_to_update = DraftUpdate(
                title=data.title,
                description=data.description,
                ingredients=json.dumps([ingredient.model_dump() for ingredient in data.ingredients]),
                instructions=data.instructions,
            )
            updated_draft = self._draft_repository.update(draft_id, draft_to_update)
            if updated_draft is None:
                db.session.rollback()
                raise NotFoundError(
                    "Rascunho não encontrado.",
                    code="DRAFT_NOT_FOUND_AFTER_UPDATE",
                )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(
                "Não foi possível atualizar o rascunho.",
                code="DRAFT_UPDATE_INTEGRITY_ERROR",
            ) from None
        except SQLAlchemyError:
            db.session.rollback()
            raise PersistenceError(
                "Falha ao persistir o rascunho.",
                code="DRAFT_UPDATE_PERSISTENCE_ERROR",
            ) from None

        return self._draft_public_mapper.map_to_public(updated_draft)

    def delete(self, draft_id: str, user_id: str) -> None:
        draft = self._draft_repository.get_by_id(draft_id)
        if draft is None:
            raise NotFoundError(
                "Rascunho não encontrado.",
                code="DRAFT_NOT_FOUND",
            )
        if draft.author_id != user_id:
            raise UnauthorizedError(
                "Você não é o criador desse rascunho.",
                code="DRAFT_NOT_OWNED",
            )
        try:
            self._draft_repository.delete(draft_id)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ConflictError(
                "Não foi possível excluir o rascunho devido a restrições de integridade no banco.",
                code="DRAFT_DELETE_INTEGRITY_ERROR",
            ) from None
        except SQLAlchemyError:
            db.session.rollback()
            raise PersistenceError(
                "Falha ao persistir a exclusão do rascunho.",
                code="DRAFT_DELETE_PERSISTENCE_ERROR",
            ) from None

    def get_all_by_author_id(
        self,
        author_id: str,
        page: int,
        per_page: int,
    ) -> PaginatedDraftsDTO:
        user = self._user_repository.get_by_id(author_id)
        if user is None:
            raise NotFoundError(
                "Usuário não encontrado.",
                code="USER_NOT_FOUND",
            )
        total_items = self._draft_repository.count_by_author_id(author_id)
        offset = (page - 1) * per_page
        drafts = self._draft_repository.get_all_by_author_id(
            author_id, offset, per_page
        )
        items = [
            self._draft_public_mapper.map_to_public(draft) for draft in drafts
        ]
        return PaginatedDraftsDTO(
            items=items,
            pagination=build_pagination_meta(page, per_page, total_items),
        )

