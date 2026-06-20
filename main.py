from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
from app.routes import menu, auth, orders, analytics, health
import os

app = FastAPI(
    title="Happy Kitchen API",
    description="Restaurant Management REST API",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
if os.getenv("PYTEST_CURRENT_TEST"):
    limiter.enabled = False

app.include_router(menu.router)
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(analytics.router)
app.include_router(health.router)

@app.get("/", tags=["System Vitals"], summary="Root system check")
@limiter.limit("100/minute")
def home(request: Request):
    return {"message": "welcome to happy kitchen"}