from pydantic import BaseModel

class MenuResponse(BaseModel):
    item_id: int
    item_name: str
    item_price: int
    category: str
    calories: int
    health_score: int

class UserRegister(BaseModel):
    user_name: str
    email: str
    password: str

class RegisterResponse(BaseModel):
    status: str
    message: str

class UserLogin(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    status: str

class placeorder(BaseModel):
    user_id: int
    item_id: int
    quantity: int

class OrderResponse(BaseModel):
    status: str
    total_bill: float

class HealthRequest(BaseModel):
    item_id: int

class HealthResponse(BaseModel):
    selected_item: str
    healthier_alternative: str
    selected_calories: int
    alternative_calories: int
    reason: str