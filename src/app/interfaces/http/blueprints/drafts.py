from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from app.application.dto.draft import (CreateDraftDTO,
                                        UpdateDraftDTO)
from app.domain.exceptions import (ConflictError, ExternalServiceError,
                                   NotFoundError, PersistenceError,
                                   UnauthorizedError)

from ..schemas import (CreateDraftSchema, PaginationSchema,
                       UpdateDraftSchema)

drafts_bp = Blueprint('drafts_bp', __name__)


def get_draft_service():
    return current_app.extensions['draft_service']


@drafts_bp.get('/')
def get_all():
    drafts = get_draft_service().get_all()
    response = [draft.model_dump(mode="json") for draft in drafts]
    return jsonify(response), 200


@drafts_bp.post('/')
def create_draft():
    data = request.get_json(silent=True) or {}
    user_id = request.headers.get('user-id')
    try:
        validated_draft = CreateDraftSchema.model_validate(data)
        dto = CreateDraftDTO.model_validate({
            **validated_draft.model_dump(),
            'user_id': user_id,
        })
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 422

    try:
        created_draft = get_draft_service().create(dto)
    except ConflictError as e:
        return (
            jsonify(
                {
                    "error": "conflict",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            409,
        )
    except NotFoundError as e:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            404,
        )
    except ValidationError:
        return (
            jsonify(
                {
                    "error": "internal_error",
                    "message": "Falha ao validar dados internos do rascunho.",
                    "code": "DRAFT_SERVICE_VALIDATION_ERROR",
                }
            ),
            500,
        )
    except ExternalServiceError as e:
        status = 422 if e.code == "UNREADABLE_FILE" else 502
        return (
            jsonify(
                {
                    "error": "external_service_error",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            status,
        )
    except PersistenceError as e:
        return (
            jsonify(
                {
                    "error": "persistence_error",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            500,
        )

    response = created_draft.model_dump(mode="json")
    return jsonify(response), 201


@drafts_bp.get('/author/<string:author_id>')
def get_author_drafts(author_id: str):
    try:
        validated = PaginationSchema.model_validate(dict(request.args))
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422

    try:
        result = get_draft_service().get_all_by_author_id(
            author_id, **validated.model_dump()
        )
    except NotFoundError as e:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            404,
        )

    return jsonify(result.model_dump(mode="json")), 200


@drafts_bp.get('/<string:draft_id>')
def get_draft_by_id(draft_id: str):
    try:
        draft = get_draft_service().get_by_id(draft_id)
    except NotFoundError as e:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            404,
        )

    response = draft.model_dump(mode="json")
    return jsonify(response), 200


@drafts_bp.put('/<string:draft_id>')
def update_draft(draft_id: str):
    data = request.get_json(silent=True) or {}
    user_id = request.headers.get('user-id')
    try:
        validated_draft = UpdateDraftSchema.model_validate(data)
        dto = UpdateDraftDTO.model_validate(validated_draft.model_dump())
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 422

    try:
        updated_draft = get_draft_service().update(draft_id, user_id, dto)
    except NotFoundError as e:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            404,
        )
    except UnauthorizedError as e:
        return (
            jsonify(
                {
                    "error": "unauthorized",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            401,
        )
    except ConflictError as e:
        return (
            jsonify(
                {
                    "error": "conflict",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            409,
        )
    except ValidationError:
        return (
            jsonify(
                {
                    "error": "internal_error",
                    "message": "Falha ao validar dados internos do rascunho.",
                    "code": "DRAFT_SERVICE_VALIDATION_ERROR",
                }
            ),
            500,
        )
    except PersistenceError as e:
        return (
            jsonify(
                {
                    "error": "persistence_error",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            500,
        )

    response = updated_draft.model_dump(mode="json")
    return jsonify(response), 200


@drafts_bp.delete('/<string:draft_id>')
def delete_draft(draft_id: str):
    user_id = request.headers.get('user-id')
    try:
        get_draft_service().delete(draft_id, user_id)
    except NotFoundError as e:
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            404,
        )
    except UnauthorizedError as e:
        return (
            jsonify(
                {
                    "error": "unauthorized",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            401,
        )
    except ConflictError as e:
        return (
            jsonify(
                {
                    "error": "conflict",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            409,
        )
    except PersistenceError as e:
        return (
            jsonify(
                {
                    "error": "persistence_error",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            500,
        )

    return '', 204
