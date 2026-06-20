import json
from fastapi import HTTPException
from app.repositories import menu_repo
from app.cache import redis_client

CACHE_KEY = "restaurant_food_menu"

def get_menu():
    try:
        cached_menu = redis_client.get(CACHE_KEY)
        if cached_menu:
            return json.loads(cached_menu)
    except Exception:
        pass
    try:
        menu = menu_repo.db_get_menu()
        if menu:
            try:
                redis_client.set(CACHE_KEY, json.dumps(menu),ex=600)
            except Exception:
                pass
        return menu
    except Exception as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))

def add_menu_item(item_name, item_price, category):
    if item_price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")
    try:
        menu_repo.db_add_menu_item(item_name, item_price, category)
        try:
            redis_client.delete(CACHE_KEY)
        except Exception:
            pass
        return {"status": "success", "message": "Item added successfully"}
    except Exception as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))

def update_menu_items(item_id, item_name, item_price, category):
    try:
        menu_repo.db_update_menu_item(item_id, item_name, item_price, category)
        try:
            redis_client.delete(CACHE_KEY)
        except Exception:
            pass
        return {"status": "updated successfully"}
    except Exception as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))

def delete_menu_item(item_id):
    try:
        menu_repo.db_delete_menu_item(item_id)
        try:
            redis_client.delete(CACHE_KEY)
        except Exception:
            pass
        return {"status": "deleted successfully"}
    except Exception as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))