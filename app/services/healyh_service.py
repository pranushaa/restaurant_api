from fastapi import HTTPException
from app.repositories import menu_repo

def healthier_alternative(item_id):
    try:
        selected_item = menu_repo.db_get_menu_item_by_id(item_id)
        if not selected_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        alternative = menu_repo.db_get_healthier_alternative(
            selected_item["category"], selected_item["health_score"]
        )
        if not alternative:
            return {
                "selected_item": selected_item["item_name"],
                "healthier_alternative": selected_item["item_name"],
                "selected_calories": selected_item["calories"],
                "alternative_calories": selected_item["calories"],
                "reason": "No healthier alternative available"
            }
        return {
            "selected_item": selected_item["item_name"],
            "healthier_alternative": alternative["item_name"],
            "selected_calories": selected_item["calories"],
            "alternative_calories": alternative["calories"],
            "reason": "Higher health score and lower calories"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))