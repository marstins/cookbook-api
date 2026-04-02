from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from app.application.dto.user import (CreateUserDTO, UpdateUserNameDTO,
                                      UpdateUserPasswordDTO)
from app.domain.exceptions import ConflictError, NotFoundError

from ..schemas import (CreateUserSchema, UpdateUserNameSchema,
                       UpdateUserPasswordSchema, UserResponseSchema)

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
        return jsonify({'errors': e.errors()}), 422

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


@users_bp.patch('/<string:user_id>/change-password')
def update_user_password(user_id: str):
    data = request.get_json(silent=True) or {}
    try:
        validated = UpdateUserPasswordSchema.model_validate(data)
        dto = UpdateUserPasswordDTO.model_validate(validated.model_dump())
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 422

    try:
        updated_user = get_user_service().update_password(user_id, dto)
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


@users_bp.patch('/<string:user_id>/change-name')
def update_user_name(user_id: str):
    data = request.get_json(silent=True) or {}
    try:
        validated = UpdateUserNameSchema.model_validate(data)
        dto = UpdateUserNameDTO.model_validate(validated.model_dump())
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 422

    try:
        updated_user = get_user_service().update_name(user_id, dto)
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
