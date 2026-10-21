from flask import Blueprint, current_app, g, jsonify, request
from pydantic import ValidationError

from app.application.dto.user import (CreateUserDTO, UpdateUserDTO,
                                      UpdateUserPasswordDTO)
from app.domain.exceptions import ConflictError, ExternalServiceError, NotFoundError

from ..schemas import (CreateUserSchema, UpdateUserSchema,
                       UpdateUserPasswordSchema, UserResponseSchema)
from ..validation import validation_error_response

users_bp = Blueprint('users_bp', __name__)


def get_user_service():
    return current_app.extensions['user_service']


@users_bp.get('/')
def get_all():
    try:
        users = get_user_service().get_all()
        response = [
            UserResponseSchema.model_validate(user).model_dump(mode="json")
            for user in users
        ]
    except ValidationError:
        return (
            jsonify(
                {
                    "error": "internal_error",
                    "message": "Falha ao serializar usuários.",
                    "code": "INTERNAL_VALIDATION_ERROR",
                }
            ),
            500,
        )

    return jsonify(response), 200


@users_bp.post('/')
def create_user():
    data = request.get_json(silent=True) or {}
    try:
        validated_user = CreateUserSchema.model_validate(data)
        dto = CreateUserDTO.model_validate(validated_user.model_dump())
    except ValidationError as e:
        return validation_error_response(e)

    try:
        created_user = get_user_service().create(dto)
        response = UserResponseSchema.model_validate(created_user).model_dump(
            mode="json"
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
                    "message": "Falha ao processar ou serializar o usuário.",
                    "code": "INTERNAL_VALIDATION_ERROR",
                }
            ),
            500,
        )

    return jsonify(response), 201


@users_bp.get('/<string:user_id>')
def get_user_by_id(user_id: str):
    try:
        user = get_user_service().get_by_id(user_id)
        response = UserResponseSchema.model_validate(user).model_dump(mode="json")
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
                    "message": "Falha ao serializar o usuário.",
                    "code": "INTERNAL_VALIDATION_ERROR",
                }
            ),
            500,
        )

    return jsonify(response), 200


@users_bp.patch('/change-password')
def update_user_password():
    data = request.get_json(silent=True) or {}
    user_id = g.user_id
    auth_id = g.auth_id
    try:
        validated = UpdateUserPasswordSchema.model_validate(data)
        dto = UpdateUserPasswordDTO.model_validate(validated.model_dump())
    except ValidationError as e:
        return validation_error_response(e)

    try:
        result = get_user_service().update_password(auth_id, user_id, dto)
        response = UserResponseSchema.model_validate(result.user).model_dump(mode="json")
        response["access_token"] = result.access_token
        response["refresh_token"] = result.refresh_token
        response["expires_at"] = result.expires_at
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
    except ExternalServiceError as e:
        return (
            jsonify(
                {
                    "error": "external_service_error",
                    "message": e.message,
                    "code": e.code,
                }
            ),
            502,
        )
    except ValidationError:
        return (
            jsonify(
                {
                    "error": "internal_error",
                    "message": "Falha ao processar ou serializar o usuário.",
                    "code": "INTERNAL_VALIDATION_ERROR",
                }
            ),
            500,
        )

    return jsonify(response), 200


@users_bp.patch('/update')
def update_user():
    data = request.get_json(silent=True) or {}
    user_id = g.user_id
    try:
        validated = UpdateUserSchema.model_validate(data)
        dto = UpdateUserDTO.model_validate(validated.model_dump())
    except ValidationError as e:
        return validation_error_response(e)

    try:
        updated_user = get_user_service().update(user_id, dto)
        response = UserResponseSchema.model_validate(updated_user).model_dump(
            mode="json"
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
                    "message": "Falha ao processar ou serializar o usuário.",
                    "code": "INTERNAL_VALIDATION_ERROR",
                }
            ),
            500,
        )

    return jsonify(response), 200


@users_bp.delete('/<string:user_id>')
def delete_user(user_id: str):
    try:
        get_user_service().delete(user_id)
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

    return '', 204
