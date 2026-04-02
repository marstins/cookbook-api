from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict


class LoginRequestSchema(BaseModel):
    model_config = ConfigDict(title='LoginRequestSchema')

    email: EmailStr = Field(min_length=5, max_length=30, title='Email do usuário')
    password: str = Field(min_length=8, max_length=30, title='Senha do usuário')
