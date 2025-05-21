from datetime import date
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette.responses import JSONResponse

from src.application.mappers import map_metric_aggregate_to_contract
from src.application.services import DatabaseHealthCheckService, GetMetricsService
from src.crosscutting import get_service, logging_scope, Logger
from src.web.contracts import MetricsResponse

print("MetricsResponse validate method:", MetricsResponse.validate)
print("MetricsResponse class file:", MetricsResponse.__module__)

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
    start_date: Optional[date] = Query('2025-06-01', description="Start date for filtering"),
    end_date: Optional[date] = Query('2025-06-30', description="End date for filtering"),
    day_range: Optional[int] = Query(30, description="Number of days before today"),
    logger: Logger = Depends(get_service(Logger)),
    get_metrics_service: GetMetricsService = Depends(get_service(GetMetricsService))
):
    id_str = str(metric_id)
    with logging_scope(
        operation=get_metrics.__name__,
        id=id_str,
        start_date=start_date,
        end_date=end_date,
        day_range=day_range,
    ):
        logger.info("Endpoint called")

        metrics = await get_metrics_service(
            _id=id_str,
            start_date=start_date,
            end_date=end_date,
            day_range=day_range
        )

        if metrics is None:
            return JSONResponse(status_code=404, content={"detail": "Metrics not found"})

        response = map_metric_aggregate_to_contract(metrics)
        return response