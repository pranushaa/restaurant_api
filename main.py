from fastapi import FastAPI
from app.routes import menu, auth, orders, analytics, health

app = FastAPI()

app.include_router(menu.router)
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(analytics.router)
app.include_router(health.router)

@app.get("/", tags=["System Vitals"], summary="Root system check")
def home():
    return {"message": "welcome to happy kitchen"}