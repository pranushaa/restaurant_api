from fastapi import HTTPException
from app.repositories import analytics_repo
import mysql.connector

def get_business_report(status=None):
    try:
        return analytics_repo.db_get_business_report(status)
    except mysql.connector.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))

def get_basic_financial_report():
    try:
        return analytics_repo.db_get_basic_financial_report()
    except mysql.connector.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))