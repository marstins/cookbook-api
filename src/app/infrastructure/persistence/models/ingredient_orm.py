import uuid

from app.infrastructure.persistence.database import db


class IngredientORM(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    description = db.Column(db.String(255), nullable=False)
    recipe_id = db.Column(
        db.String(36),
        db.ForeignKey('recipes.id', ondelete="CASCADE"),
        nullable=False,
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    recipe = db.relationship('RecipeORM', back_populates='ingredients')
