from fastapi import APIRouter
from typing import List
from app.models import MenuResponse
from app.services import menu_services

router = APIRouter(tags=["Menu Management"])

@router.get("/menu", response_model=List[MenuResponse])
def get_menu():
    return menu_services.get_menu()

@router.post("/menu")
def add_menu_item(item_name: str, item_price: int, category: str):
    return menu_services.add_menu_item(item_name, item_price, category)

@router.put("/menu/{item_id}")
def update_menu_items(item_id: int, item_name: str, item_price: int, category: str):
    return menu_services.update_menu_items(item_id, item_name, item_price, category)

@router.delete("/menu/{item_id}")
def delete_menu_item(item_id: int):
    return menu_services.delete_menu_item(item_id)