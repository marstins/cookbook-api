from pydantic import BaseModel

from datetime import datetime

from app.domain.models.aggregates.user.user import UserPublic


class AuthResponse(BaseModel):
    user: UserPublic
    access_token: str
    refresh_token: str
    expires_at: datetime