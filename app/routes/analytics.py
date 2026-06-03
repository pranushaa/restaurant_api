from fastapi import APIRouter
from app.services import analytics_service

router = APIRouter(tags=["Business Intelligence Analytics"])

@router.get("/analytics/report")
def get_business_report(status: str = None):
    return analytics_service.get_business_report(status)

@router.get("/analytics/basic-report")
def get_basic_financial_report():
    return analytics_service.get_basic_financial_report()