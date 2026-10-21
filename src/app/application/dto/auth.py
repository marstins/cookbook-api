from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.domain.models.aggregates.user import UserPublic


class LoginDTO(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenDTO(BaseModel):
    refresh_token: str


class LoginResultDTO(BaseModel):
    user: UserPublic
    access_token: str
    refresh_token: str
    expires_at: datetime
