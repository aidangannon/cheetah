from datetime import date
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette.responses import JSONResponse

from src import core
from src.application.mappers import map_metric_aggregate_to_contract, map_metric_configuration_contract_to_domain
from src.application.services import DatabaseHealthCheckService, GetMetricsService, CreateMetricConfigurationService
from src.core import MetricConfigurationAggregate
from src.crosscutting import get_service, logging_scope, Logger
from src.web.contracts import MetricsResponse, HealthCheckResponse, CreatedResponse, CreateMetricConfiguration

health_router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@health_router.get(
    "/",
    response_model=HealthCheckResponse,
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
    responses={
        404: {"description": "Metric not found"}
    },
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
    
metrics_configuration_router = APIRouter(
    prefix="/metric-configuration",
    tags=["MetricConfiguration"]
)

@metrics_configuration_router.post(
    "/",
    response_model=CreatedResponse,
    summary="Create metric configuration",
    description="Create metric configuration and do query generation"
)
async def create_metrics_configuration(
    create_metric_configuration: CreateMetricConfiguration,
    logger: Logger = Depends(get_service(Logger)),
    create_metric_configuration_service: CreateMetricConfigurationService = Depends(get_service(CreateMetricConfigurationService))
):
    with logging_scope(
        operation=create_metrics_configuration.__name__,
        is_editable=create_metric_configuration.is_editable,
        query_generation_prompt=create_metric_configuration.query_generation_prompt
    ):
        logger.info("Endpoint called")

        _id = await create_metric_configuration_service(map_metric_configuration_contract_to_domain(create_metric_configuration))

        return CreatedResponse(id=_id)