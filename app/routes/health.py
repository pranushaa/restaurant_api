from fastapi import APIRouter, Body
from app.models import HealthRequest, HealthResponse
from app.services import healyh_service

router = APIRouter(tags=["Smart Recommendations"])

@router.post("/healthier-alternative", response_model=HealthResponse, summary="Suggest a healthier food alternative")
def healthier_alternative(data: HealthRequest = Body(...)):
    """Suggests a healthier option in the same category with higher health score and lower calories."""
    return healyh_service.healthier_alternative(data.item_id)