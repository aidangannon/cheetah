from datetime import date
from typing import Optional
from unittest.mock import Mock
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from src.application.mappers import map_metric_aggregate_to_contract, map_metric_configuration_contract_to_domain, \
    map_metric_record_contract_to_domain
from src.application.services import DatabaseHealthCheckService, GetMetricsService, CreateMetricConfigurationService, \
    CreateMetricService
from src.crosscutting import get_service, logging_scope, Logger
from src.infrastructure import Settings
from src.infrastructure.auth import CognitoAuthenticator
from src.web import auth_provider
from src.web.contracts import MetricsResponse, HealthCheckResponse, CreatedResponse, CreateMetricConfigurationRequest, \
    CreateMetricRequest

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
    health_check_service: DatabaseHealthCheckService = Depends(get_service(DatabaseHealthCheckService)),
    payload: dict = Depends(auth_provider)
):
    with logging_scope(operation=get_health.__name__):
        logger.info(f"Running health checks for {payload['sub']}")
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
        HTTP_404_NOT_FOUND: {"description": "Metric not found"}
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
    
@metrics_router.post(
    "/",
    response_model=CreatedResponse,
    status_code=HTTP_201_CREATED,
    summary="Create metric configuration",
    description="Create metric configuration and do query generation"
)
async def create_metrics_configuration(
    create_metric_configuration: CreateMetricConfigurationRequest,
    logger: Logger = Depends(get_service(Logger)),
    create_metric_configuration_service: CreateMetricConfigurationService = Depends(get_service(CreateMetricConfigurationService))
):
    with logging_scope(
        operation=create_metrics_configuration.__name__,
        is_editable=create_metric_configuration.is_editable,
        query_generation_prompt=create_metric_configuration.query_generation_prompt
    ):
        logger.info("Endpoint called")

        _id = await create_metric_configuration_service(
            map_metric_configuration_contract_to_domain(create_metric_configuration),
            create_metric_configuration.query_generation_prompt
        )

        return CreatedResponse(id=_id)


@metrics_router.post(
    "/{metric_id}/metric-records",
    status_code=HTTP_201_CREATED,
    summary="Create metric record",
    description="Create metric data for a given metric type"
)
async def create_metric_record(
    metric_id: UUID,
    create_metric_data: CreateMetricRequest,
    logger: Logger = Depends(get_service(Logger)),
    create_metric_data_service: CreateMetricService = Depends(get_service(CreateMetricService))
):
    str_metric_id = str(metric_id)
    with logging_scope(
        operation=create_metric_record.__name__,
        metric_id=str_metric_id,
        obsolescence=create_metric_data.obsolescence,
        obsolescence_val=create_metric_data.obsolescence_val,
        alert_type=create_metric_data.alert_type,
        alert_category=create_metric_data.alert_category
    ):
        logger.info("Endpoint called")

        _id = await create_metric_data_service(
            str_metric_id,
            map_metric_record_contract_to_domain(create_metric_data),
        )

        if _id is None:
            return JSONResponse(status_code=404, content={"detail": "Metric not found"})

        return Response(status_code=201)