import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)


async def is_database_available(session: AsyncSession) -> bool:
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        logger.exception("database_health_check_failed")
        return False
    return True
