from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

from app.application.mappers.recipe_mapper import RecipePublicMapper
from app.application.mappers.user_mapper import UserPublicMapper
from app.application.mappers.draft_mapper import DraftPublicMapper
from app.core.config import Config
from app.infrastructure.persistence import \
    models as _persistence_models  # noqa: F401
from app.infrastructure.persistence.database import db
from app.infrastructure.persistence.mappers.draft_mapper import DraftMapper
from app.infrastructure.persistence.mappers.recipe_mapper import RecipeMapper
from app.infrastructure.persistence.repositories import (DraftRepository,
                                                         IngredientRepository,
                                                         RecipeRepository,
                                                         UserRepository)
from app.infrastructure.security.password_hasher import PasswordHasher
from app.interfaces.http.blueprints.auth import auth_bp
from app.interfaces.http.blueprints.recipes import recipes_bp
from app.interfaces.http.blueprints.users import users_bp
from app.interfaces.http.blueprints.drafts import drafts_bp
from app.interfaces.http.openapi import register_openapi_routes
from app.seed import seed_command
from app.services.auth_service import AuthService
from app.services.recipe_service import RecipeService
from app.services.user_service import UserService
from app.services.draft_service import DraftService
from app.services.decode_draft_image_service import DecodeDraftImageService

_repo_root = Path(__file__).resolve().parent.parent.parent
_instance_dir = _repo_root / "instance"

app = Flask(
    __name__,
    instance_path=str(_instance_dir),
    instance_relative_config=True,
)
app.config.from_object(Config)
app.json.sort_keys = False
CORS(app)
db.init_app(app)


@app.errorhandler(RequestEntityTooLarge)
def handle_request_too_large(_error):
    return (
        jsonify(
            {
                "error": "payload_too_large",
                "message": "O arquivo enviado é grande demais.",
                "code": "REQUEST_TOO_LARGE",
            }
        ),
        413,
    )

with app.app_context():
    db.create_all()

password_hasher = PasswordHasher()
recipe_mapper = RecipeMapper()
recipe_public_mapper = RecipePublicMapper()
user_public_mapper = UserPublicMapper()
draft_public_mapper = DraftPublicMapper()
user_repository = UserRepository()
ingredient_repository = IngredientRepository()
recipe_repository = RecipeRepository(recipe_mapper)
user_service = UserService(
    user_repository,
    password_hasher,
    user_public_mapper,
    recipe_repository,
    ingredient_repository,
)
recipe_service = RecipeService(
    recipe_repository,
    recipe_public_mapper,
    user_repository,
    ingredient_repository,
)
auth_service = AuthService(user_repository, password_hasher, user_public_mapper)
draft_mapper = DraftMapper()
draft_repository = DraftRepository(draft_mapper)
decode_draft_image_service = DecodeDraftImageService(Config.OCR_SPACE_API_KEY)
draft_service = DraftService(
    draft_repository,
    draft_public_mapper,
    user_repository,
    decode_draft_image_service,
)

app.extensions["user_service"] = user_service
app.extensions["recipe_service"] = recipe_service
app.extensions["auth_service"] = auth_service
app.extensions["draft_service"] = draft_service

app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(recipes_bp, url_prefix='/recipes')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(drafts_bp, url_prefix='/drafts')

register_openapi_routes(app)
app.cli.add_command(seed_command)


@app.route("/")
def home():
    return "Cookbook API"
