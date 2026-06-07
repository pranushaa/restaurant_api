from fastapi import APIRouter, Body, Depends
from app.models import placeorder, OrderResponse
from app.services import order_service
from app.dependencies import verify_token

router = APIRouter(tags=["Transactional Orders"])

@router.post("/orders", response_model=OrderResponse, summary="Place a live food order", dependencies=[Depends(verify_token)])
def place_new_order(order_data: placeorder = Body(...)):
    """Place order with ACID transaction. Requires JWT token."""
    return order_service.place_new_order(order_data.user_id, order_data.item_id, order_data.quantity)

@router.get("/orders/{user_id}", summary="Fetch paginated order history")
def get_order_history(user_id: int, page: int = 1, limit: int = 5, order_status: str = None):
    """Get order history with pagination."""
    return order_service.get_order_history(user_id, page, limit, order_status)