from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from src.application.services import DatabaseHealthCheckService, GetMetricsService
from src.crosscutting import get_service, logging_scope, Logger
from src.web.contracts import MetricsResponse

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

metrics_router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"]
)

@metrics_router.get(
    "/{metric_id}",
    response_model=MetricsResponse,
    summary="Get metrics",
    description="Get metrics configuration, data and layouts"
)
async def get_metrics(
    metric_id: UUID,
    logger: Logger = Depends(get_service(Logger)),
    get_metrics_service: GetMetricsService = Depends(get_service(GetMetricsService))
):
    id_str = str(metric_id)
    with logging_scope(operation=get_metrics.__name__, id=id_str):
        logger.info("Endpoint called")
        metrics = await get_metrics_service(_id=id_str)
        if metrics is None:
            return JSONResponse(status_code=404, content={"detail": "Metrics not found"})
        return None