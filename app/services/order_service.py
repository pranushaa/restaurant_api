import logging
from fastapi import HTTPException
from app.repositories import order_repo

logger = logging.getLogger(__name__)

def place_new_order(user_id, item_id, quantity):
    if quantity <= 0:
        logger.warning(f"Invalid quantity {quantity} from user {user_id}")
        raise HTTPException(status_code=400, detail="Quantity must be > 0")
    try:
        menu = order_repo.db_get_item_price(item_id)
        if not menu:
            logger.warning(f"Item {item_id} not found")
            raise HTTPException(status_code=404, detail="Food item not found in menu")
        calculated_total = menu['item_price'] * quantity
        order_repo.db_insert_order(user_id, item_id, quantity, calculated_total)
        logger.info(f"Order placed by user {user_id}, total {calculated_total}")
        return {"status": "Order Placed Successfully!", "total_bill": float(calculated_total)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Order failed for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transaction failed. Order rolled back: {str(e)}")

def get_order_history(user_id, page, limit, order_status=None):
    try:
        offset = (page - 1) * limit
        history = order_repo.db_get_order_history(user_id, limit, offset, order_status)
        logger.info(f"Order history fetched for user {user_id}, page {page}")
        return {"page": page, "limit": limit, "data": history}
    except Exception as e:
        logger.error(f"Order history failed for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))