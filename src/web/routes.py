from typing import Any

from fastapi import APIRouter, Depends

from src.application.services import DatabaseHealthCheckService
from src.crosscutting import get_service, logging_scope, Logger

health_router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@health_router.get(
    "/",
    response_model=dict[str, Any],
    summary="Run health checks",
    description="Health checks application and db"
)
async def get_health(
    logger: Logger = Depends(get_service(Logger)),
    health_check_service: DatabaseHealthCheckService = Depends(get_service(DatabaseHealthCheckService))
):
    with logging_scope(operation=get_health.__name__):
        logger.info("Endpoint called")
        database_result = await health_check_service()
        return {"application": True, "database": database_result}