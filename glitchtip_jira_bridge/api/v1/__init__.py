from fastapi import APIRouter

from .alert import router as alert_router

router = APIRouter()
router.include_router(alert_router)


@router.get("/")
def index() -> dict:
    return {"message": "Ready"}
