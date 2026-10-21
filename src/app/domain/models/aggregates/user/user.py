from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    auth_id: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None


class UserPublic(UserBase):
    id: str
    created_at: datetime


class User(UserBase):
    id: str
    created_at: datetime

