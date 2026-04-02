from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict


class CreateUserSchema(BaseModel):
    model_config = ConfigDict(title='CreateUserSchema')

    name: str = Field(min_length=5, max_length=20, title='Nome do usuário')
    email: EmailStr = Field(min_length=5, max_length=30, title='Email do usuário')
    password: str = Field(min_length=8, max_length=30, title='Senha do usuário')


class UpdateUserPasswordSchema(BaseModel):
    model_config = ConfigDict(title='UpdateUserPasswordSchema')

    email: EmailStr = Field(min_length=5, max_length=30, title='Email do usuário')
    old_password: str = Field(min_length=8, max_length=30, title='Senha antiga do usuário')
    new_password: str = Field(min_length=8, max_length=30, title='Senha nova do usuário')


class UpdateUserNameSchema(BaseModel):
    model_config = ConfigDict(title='UpdateUserNameSchema')

    email: EmailStr = Field(min_length=5, max_length=30, title='Email do usuário')
    new_name: str = Field(min_length=5, max_length=20, title='Nome novo do usuário')


class UserResponseSchema(BaseModel):
    model_config = ConfigDict(title='UserResponseSchema', from_attributes=True)

    id: str = Field(max_length=36, title='Id do usuário')
    name: str = Field(min_length=5, max_length=20, title='Nome do usuário')
    email: EmailStr = Field(min_length=5, max_length=30, title='Email do usuário')
    created_at: datetime = Field(title='Data de criação do usuário')
