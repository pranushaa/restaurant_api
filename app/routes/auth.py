from fastapi import APIRouter, Body
from app.models import UserRegister, RegisterResponse, UserLogin, LoginResponse
from app.services import auth_service

router = APIRouter(tags=["Identity & Security"])

@router.post("/register", response_model=RegisterResponse)
def register_user(user: UserRegister = Body(...)):
    return auth_service.register_user(user.user_name, user.email, user.password)

@router.post("/login", response_model=LoginResponse)
def login_user(user_data: UserLogin = Body(...)):
    return auth_service.login_user(user_data.email, user_data.password)