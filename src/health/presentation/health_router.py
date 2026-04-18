from fastapi import APIRouter
from src.health.application.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])

_service = HealthService()


@router.get("")
def get_health():
    result = _service.check()
    return {"status": result.status, "timestamp": result.timestamp}
