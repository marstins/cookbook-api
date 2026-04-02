from sqlalchemy import select

from app.domain.models.aggregates.user import User, UserCreate
from app.infrastructure.persistence.database import db
from app.infrastructure.persistence.models.user_orm import UserORM


class UserRepository:
    def get_all(self) -> list[User]:
        users = db.session.scalars(select(UserORM).order_by(UserORM.created_at)).all()
        return [User.model_validate(user, from_attributes=True) for user in users]


    def create(self, data: UserCreate) -> User:
        user = UserORM(**data.model_dump())
        db.session.add(user)
        db.session.flush()
        db.session.refresh(user)
        return User.model_validate(user, from_attributes=True)


    def get_by_email(self, user_email: str) -> User | None:
        user = db.session.scalar(
            select(UserORM).where(UserORM.email == user_email)
        )
        if user is None:
            return None
        return User.model_validate(user, from_attributes=True)


    def get_by_name(self, user_name: str) -> User | None:
        user = db.session.scalar(
            select(UserORM).where(UserORM.name == user_name)
        )
        if user is None:
            return None
        return User.model_validate(user, from_attributes=True)


    def get_by_id(self, user_id: str) -> User | None:
        user = db.session.scalar(
            select(UserORM).where(UserORM.id == user_id)
        )
        if user is None:
            return None
        return User.model_validate(user, from_attributes=True)


    def update_password(self, user_id: str, password_hash: str) -> User | None:
        user_orm = db.session.scalar(
            select(UserORM).where(UserORM.id == user_id)
        )
        if user_orm is None:
            return None
        user_orm.password_hash = password_hash
        db.session.flush()
        db.session.refresh(user_orm)
        return User.model_validate(user_orm, from_attributes=True)


    def update_name(self, user_id: str, user_name: str) -> User | None:
        user_orm = db.session.scalar(
            select(UserORM).where(UserORM.id == user_id)
        )
        if user_orm is None:
            return None
        user_orm.name = user_name
        db.session.flush()
        db.session.refresh(user_orm)
        return User.model_validate(user_orm, from_attributes=True)


    def delete(self, user_id: str) -> bool:
        user = db.session.scalar(
            select(UserORM).where(UserORM.id == user_id)
        )
        if user is None:
            return False
        db.session.delete(user)
        db.session.flush()
        return True
