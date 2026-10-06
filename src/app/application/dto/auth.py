from pydantic import BaseModel, EmailStr

from app.domain.models.aggregates.user import UserPublic


class LoginDTO(BaseModel):
    email: EmailStr
    password: str


class LoginResultDTO(BaseModel):
    user: UserPublic
    token: str
