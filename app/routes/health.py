from fastapi import APIRouter, Body
from app.models import HealthRequest, HealthResponse
from app.services import healyh_service

router = APIRouter(tags=["Smart Recommendations"])

@router.post("/healthier-alternative", response_model=HealthResponse)
def healthier_alternative(data: HealthRequest = Body(...)):
    return healyh_service.healthier_alternative(data.item_id)