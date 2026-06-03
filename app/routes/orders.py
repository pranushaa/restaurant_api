from fastapi import APIRouter, Body
from app.models import placeorder, OrderResponse
from app.services import order_service

router = APIRouter(tags=["Transactional Orders"])

@router.post("/orders", response_model=OrderResponse)
def place_new_order(order_data: placeorder = Body(...)):
    return order_service.place_new_order(order_data.user_id, order_data.item_id, order_data.quantity)

@router.get("/orders/{user_id}")
def get_order_history(user_id: int, page: int = 1, limit: int = 5, order_status: str = None):
    return order_service.get_order_history(user_id, page, limit, order_status)