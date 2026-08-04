from fastapi import APIRouter, Response, status

from app.api.dependencies import SessionDep
from app.schemas.health import HealthResponse, HealthStatus
from app.services.health import is_database_available

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    operation_id="getHealth",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "The database is unavailable.",
            "model": HealthResponse,
        }
    },
)
async def get_health(response: Response, session: SessionDep) -> HealthResponse:
    if await is_database_available(session):
        return HealthResponse(status=HealthStatus.HEALTHY)

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(status=HealthStatus.UNAVAILABLE)
