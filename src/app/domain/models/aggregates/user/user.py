from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password_hash: str


class UserPublic(UserBase):
    id: str
    created_at: datetime


class User(UserBase):
    id: str
    password_hash: str
    created_at: datetime
