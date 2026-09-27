import uuid

from app.infrastructure.persistence.database import db


class DraftORM(db.Model):
    __tablename__ = 'drafts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=True, default=False)
    author_id = db.Column(
        db.String(36),
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False,
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())
