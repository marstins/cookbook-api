from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from app.application.dto.auth import LoginDTO, RefreshTokenDTO

from ..schemas import LoginRequestSchema, RefreshTokenRequestSchema, UserResponseSchema
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
    response["access_token"] = result.access_token
    response["refresh_token"] = result.refresh_token
    response["expires_at"] = result.expires_at
    return jsonify(response), 200

@auth_bp.post('/refresh-token')
def refresh_token():
    data = request.get_json(silent=True) or {}
    try:
        validated_refresh = RefreshTokenRequestSchema.model_validate(data)
        dto = RefreshTokenDTO.model_validate(validated_refresh.model_dump())
        result = get_auth_service().refresh_token(dto)
    except ValidationError as e:
        return validation_error_response(e)

    response = UserResponseSchema.model_validate(result.user).model_dump(mode="json")
    response["access_token"] = result.access_token
    response["refresh_token"] = result.refresh_token
    response["expires_at"] = result.expires_at
    return jsonify(response), 200
