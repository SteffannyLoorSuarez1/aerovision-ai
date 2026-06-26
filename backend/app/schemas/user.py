from pydantic import BaseModel, EmailStr, field_validator


class UserRegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str

    @field_validator('nombre')
    @classmethod
    def nombre_not_empty(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str
