from fastapi import APIRouter
from app.services import analytics_service

router = APIRouter(tags=["Business Intelligence Analytics"])

@router.get("/analytics/report", summary="Get order counts grouped by status")
def get_business_report(status: str = None):
    """Returns order counts grouped by fulfillment status. Filter by status optionally."""
    return analytics_service.get_business_report(status)

@router.get("/analytics/basic-report", summary="Get gross revenue metrics")
def get_basic_financial_report():
    """Returns total revenue, total orders, and unique customer count."""
    return analytics_service.get_basic_financial_report()