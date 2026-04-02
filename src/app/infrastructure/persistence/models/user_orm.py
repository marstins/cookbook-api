import uuid

from app.infrastructure.persistence.database import db


class UserORM(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    created_recipes = db.relationship(
        "RecipeORM",
        back_populates="author",
        cascade="all, delete-orphan",
        foreign_keys="RecipeORM.author_id",
        passive_deletes=True,
    )

    original_recipe_author = db.relationship(
        "RecipeORM",
        back_populates="original_author",
        foreign_keys="RecipeORM.original_author_id",
    )
