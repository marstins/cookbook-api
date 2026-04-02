from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from app.application.dto.recipe import (CreateRecipeDTO, SaveRecipeDTO,
                                        UpdateRecipeDTO)
from app.domain.exceptions import (ConflictError, NotFoundError,
                                   PersistenceError)

from ..schemas import (CreateRecipeSchema, PaginationSchema, SaveRecipeSchema,
                       UpdateRecipeSchema)

recipes_bp = Blueprint('recipes_bp', __name__)


def get_recipe_service():
    return current_app.extensions['recipe_service']


@recipes_bp.get('/')
def get_all():
    recipes = get_recipe_service().get_all()
    response = [recipe.model_dump(mode="json") for recipe in recipes]
    return jsonify(response), 200


@recipes_bp.post('/')
def create_recipe():
    data = request.get_json(silent=True) or {}
    user_id = request.headers.get('user-id')
    try:
        validated_recipe = CreateRecipeSchema.model_validate(data)
        dto = CreateRecipeDTO.model_validate({
            **validated_recipe.model_dump(),
            'user_id': user_id,
        })
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 422

    try:
        created_recipe = get_recipe_service().create(dto)
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
                    "message": "Falha ao validar dados internos da receita.",
                    "code": "RECIPE_SERVICE_VALIDATION_ERROR",
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

    response = created_recipe.model_dump(mode="json")
    return jsonify(response), 201


@recipes_bp.get('/discover')
def discover_recipes():
    user_id = request.headers.get('user-id')
    try:
        validated = PaginationSchema.model_validate(dict(request.args))
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422

    result = get_recipe_service().get_all_public(
        user_id,
        **validated.model_dump(),
    )
    return jsonify(result.model_dump(mode="json")), 200


@recipes_bp.get('/author/<string:author_id>')
def get_author_recipes(author_id: str):
    try:
        validated = PaginationSchema.model_validate(dict(request.args))
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422

    try:
        result = get_recipe_service().get_all_by_author_id(
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


@recipes_bp.post('/save')
def save_recipe():
    data = request.get_json(silent=True) or {}
    user_id = request.headers.get('user-id')
    try:
        validated_recipe = SaveRecipeSchema.model_validate(data)
        dto = SaveRecipeDTO.model_validate({
            **validated_recipe.model_dump(),
            "user_id": user_id,
        })
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 422

    try:
        saved_recipe = get_recipe_service().save(dto)
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
                    "message": "Falha ao validar dados internos da receita.",
                    "code": "RECIPE_SERVICE_VALIDATION_ERROR",
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

    response = saved_recipe.model_dump(mode="json")
    return jsonify(response), 201


@recipes_bp.get('/<string:recipe_id>')
def get_recipe_by_id(recipe_id: str):
    try:
        recipe = get_recipe_service().get_by_id(recipe_id)
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

    response = recipe.model_dump(mode="json")
    return jsonify(response), 200


@recipes_bp.put('/<string:recipe_id>')
def update_recipe(recipe_id: str):
    data = request.get_json(silent=True) or {}
    try:
        validated_recipe = UpdateRecipeSchema.model_validate(data)
        dto = UpdateRecipeDTO.model_validate(validated_recipe.model_dump())
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 422

    try:
        updated_recipe = get_recipe_service().update(recipe_id, dto)
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
                    "message": "Falha ao validar dados internos da receita.",
                    "code": "RECIPE_SERVICE_VALIDATION_ERROR",
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

    response = updated_recipe.model_dump(mode="json")
    return jsonify(response), 200


@recipes_bp.delete('/<string:recipe_id>')
def delete_recipe(recipe_id: str):
    try:
        get_recipe_service().delete(recipe_id)
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
