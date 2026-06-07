from fastapi import APIRouter
from typing import List
from app.models import MenuResponse
from app.services import menu_services

router = APIRouter(tags=["Menu Management"])

@router.get("/menu", response_model=List[MenuResponse], summary="Fetch entire food menu")
def get_menu():
    """Fetch all menu items. Results are cached in Redis for 10 minutes."""
    return menu_services.get_menu()

@router.post("/menu", summary="Add a new dish to the menu")
def add_menu_item(item_name: str, item_price: int, category: str):
    """Add a new food item. Clears Redis cache automatically."""
    return menu_services.add_menu_item(item_name, item_price, category)

@router.put("/menu/{item_id}", summary="Update an existing menu item")
def update_menu_items(item_id: int, item_name: str, item_price: int, category: str):
    """Update food item by ID. Clears Redis cache automatically."""
    return menu_services.update_menu_items(item_id, item_name, item_price, category)

@router.delete("/menu/{item_id}", summary="Remove a dish from the menu")
def delete_menu_item(item_id: int):
    """Delete a food item by ID. Clears Redis cache automatically."""
    return menu_services.delete_menu_item(item_id)