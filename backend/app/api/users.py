from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse
from app.services.user_service import register_user, authenticate_user

router = APIRouter()


@router.post("/register", status_code=201)
def register(data: UserRegisterRequest):
    user_id = register_user(data.nombre, data.email, data.password)
    return {"message": "Usuario registrado exitosamente", "user_id": user_id}


@router.post("/login", response_model=UserResponse)
def login(data: UserLoginRequest):
    return authenticate_user(data.email, data.password)
