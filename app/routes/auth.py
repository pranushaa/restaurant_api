from fastapi import APIRouter, Body, Request
from app.models import UserRegister, RegisterResponse, UserLogin, LoginResponse
from app.services import auth_service
from app.limiter import limiter

router = APIRouter(tags=["Identity & Security"])

@router.post("/register", response_model=RegisterResponse, summary="Register a new customer account")
def register_user(user: UserRegister = Body(...)):
    """Register new user. Password is hashed with bcrypt before saving."""
    return auth_service.register_user(user.user_name, user.email, user.password)

@router.post("/login", response_model=LoginResponse, summary="Login and receive JWT token")
@limiter.limit("5/minute")
def login_user(request: Request, user_data: UserLogin = Body(...)):
    """Authenticate user. Returns JWT token valid for 30 minutes. Rate limited to 5 attempts per minute."""
    return auth_service.login_user(user_data.email, user_data.password)