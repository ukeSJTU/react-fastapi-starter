from enum import StrEnum

from app.schemas.base import BaseSchema


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    UNAVAILABLE = "unavailable"


class HealthResponse(BaseSchema):
    status: HealthStatus
