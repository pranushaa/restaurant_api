from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.routes import menu, auth, orders, analytics, health

security = HTTPBearer()

app = FastAPI(
    title="Happy Kitchen API",
    description="Restaurant Management REST API",
    version="1.0.0"
)

app.include_router(menu.router)
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(analytics.router)
app.include_router(health.router)

@app.get("/", tags=["System Vitals"], summary="Root system check")
def home():
    return {"message": "welcome to happy kitchen"}