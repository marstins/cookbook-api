from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from app.application.dto.auth import LoginDTO

from ..schemas import LoginRequestSchema, UserResponseSchema
from ..validation import validation_error_response

auth_bp = Blueprint('auth_bp', __name__)


def get_auth_service():
    return current_app.extensions['auth_service']


@auth_bp.post('/')
def login():
    data = request.get_json(silent=True) or {}
    try:
        validated_login = LoginRequestSchema.model_validate(data)
        dto = LoginDTO.model_validate(validated_login.model_dump())
        result = get_auth_service().login(dto)
    except ValidationError as e:
        return validation_error_response(e)

    response = UserResponseSchema.model_validate(result.user).model_dump(mode="json")
    response["token"] = result.token
    return jsonify(response), 200
