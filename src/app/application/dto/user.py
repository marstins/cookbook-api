from pydantic import BaseModel, EmailStr


class CreateUserDTO(BaseModel):
    name: str
    email: EmailStr
    password: str


class UpdateUserPasswordDTO(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str


class UpdateUserDTO(BaseModel):
    name: str | None = None
