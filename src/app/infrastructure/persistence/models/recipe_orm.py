import uuid

from app.infrastructure.persistence.database import db


class RecipeORM(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    author_id = db.Column(
        db.String(36),
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False,
    )
    original_recipe_id = db.Column(
        db.String(36),
        db.ForeignKey('recipes.id', ondelete="SET NULL"),
        nullable=True,
    )
    original_author_id = db.Column(
        db.String(36),
        db.ForeignKey('users.id', ondelete="SET NULL"),
        nullable=True,
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    ingredients = db.relationship(
        "IngredientORM",
        back_populates="recipe",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    author = db.relationship(
        "UserORM",
        back_populates="created_recipes",
        foreign_keys=[author_id],
    )

    original_author = db.relationship(
        "UserORM",
        back_populates="original_recipe_author",
        foreign_keys=[original_author_id],
    )
