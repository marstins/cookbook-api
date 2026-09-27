from app.interfaces.http.blueprints.auth import auth_bp
from app.interfaces.http.blueprints.recipes import recipes_bp
from app.interfaces.http.blueprints.users import users_bp
from app.interfaces.http.blueprints.drafts import drafts_bp

__all__ = ["auth_bp", "recipes_bp", "users_bp", "drafts_bp"]
