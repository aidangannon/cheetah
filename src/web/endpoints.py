from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Body, Path
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from src.application.mappers import map_dataset_aggregate_to_contract, map_dataset_config_contract_to_domain, \
    map_datapoint_contract_to_domain
from src.application.services import SystemStatusChecker, DataRetrievalHandler, ConfigurationManager, \
    DataPointCreationService
from src.crosscutting import get_service, logging_scope, Logger
from src.web import auth_provider, Authenticator
from src.web.models import AnalyticsResponseSchema, SystemStatusSchema, ResourceCreatedSchema, ConfigurationCreateSchema, \
    DataEntryCreateSchema

status_router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@status_router.get(
    "/",
    response_model=SystemStatusSchema,
    summary="Run health checks",
    description="Health checks application and db"
)
async def get_system_health(
    logger: Logger = Depends(get_service(Logger)),
    health_check_service: SystemStatusChecker = Depends(get_service(SystemStatusChecker))
):
    with logging_scope(operation=get_system_health.__name__):
        logger.info("Endpoint called")
        database_result = await health_check_service()
        return {"application": True, "database": database_result}

analytics_router = APIRouter(
    prefix="/data",
    tags=["Data"]
)

@analytics_router.get(
    "/{dataset_id}",
    response_model=AnalyticsResponseSchema,
    responses={
        HTTP_404_NOT_FOUND: {"description": "Dataset not found"},
        HTTP_401_UNAUTHORIZED: {"description": "Unauthenticated"},
        HTTP_403_FORBIDDEN: {"description": "Token invalid"}
    },
    summary="Get dataset",
    description="Get dataset configuration, data and layouts"
)
async def get_analytics_dataset(
    dataset_id: UUID = Path(description="dataset configuration id to search under"),
    start_date: Optional[date] = Query('2025-06-01', description="Start date for filtering"),
    end_date: Optional[date] = Query('2025-06-30', description="End date for filtering"),
    day_range: Optional[int] = Query(30, description="Number of days before today"),
    get_dataset_service: DataRetrievalHandler = Depends(get_service(DataRetrievalHandler)),
    _ = Depends(auth_provider),
    logger: Logger = Depends(get_service(Logger))
):
    id_str = str(dataset_id)
    with logging_scope(
        operation=get_analytics_dataset.__name__,
        id=id_str,
        start_date=start_date,
        end_date=end_date,
        day_range=day_range,
    ):
        logger.info("Endpoint called")

        dataset = await get_dataset_service(
            _id=id_str,
            start_date=start_date,
            end_date=end_date,
            day_range=day_range
        )

        if dataset is None:
            return JSONResponse(status_code=404, content={"detail": "Dataset not found"})

        response = map_dataset_aggregate_to_contract(dataset)
        return response
    
@analytics_router.post(
    "/",
    response_model=ResourceCreatedSchema,
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_401_UNAUTHORIZED: {"description": "Unauthenticated"},
        HTTP_403_FORBIDDEN: {"description": "Token invalid"}
    },
    summary="Create dataset configuration",
    description="Create dataset configuration and do statement generation"
)
async def create_analytics_configuration(
    create_dataset_config: ConfigurationCreateSchema = Body(..., description="dataset configuration data"),
    create_dataset_service: ConfigurationManager = Depends(get_service(ConfigurationManager)),
    _ = Depends(auth_provider),
    logger: Logger = Depends(get_service(Logger)),
):
    with logging_scope(
        operation=create_analytics_configuration.__name__,
        is_mutable=create_dataset_config.is_mutable,
        statement_generation_prompt=create_dataset_config.statement_generation_prompt
    ):
        logger.info("Endpoint called")

        _id = await create_dataset_service(
            map_dataset_config_contract_to_domain(create_dataset_config),
            create_dataset_config.statement_generation_prompt
        )

        return ResourceCreatedSchema(id=_id)


@analytics_router.post(
    "/{dataset_id}/data-points",
    status_code=HTTP_201_CREATED,
    responses={
        HTTP_401_UNAUTHORIZED: {"description": "Unauthenticated"},
        HTTP_403_FORBIDDEN: {"description": "Token invalid"}
    },
    summary="Create data point",
    description="Create data point for a given dataset type"
)
async def create_analytics_data_point(
    dataset_id: UUID = Path(description="id of the dataset configuration the data will sit under"),
    create_data_point: DataEntryCreateSchema = Body(..., description="data fields for the data point"),
    create_data_point_service: DataPointCreationService = Depends(get_service(DataPointCreationService)),
    _ = Depends(auth_provider),
    logger: Logger = Depends(get_service(Logger))
):
    str_dataset_id = str(dataset_id)
    with logging_scope(
        operation="create_data_point",
        dataset_id=str_dataset_id,
        decay_rate=create_data_point.decay_rate,
        decay_value=create_data_point.decay_value,
        notification_type=create_data_point.notification_type,
        notification_category=create_data_point.notification_category
    ):
        logger.info("Endpoint called")

        _id = await create_data_point_service(
            str_dataset_id,
            map_datapoint_contract_to_domain(create_data_point),
        )

        if _id is None:
            return JSONResponse(status_code=404, content={"detail": "Dataset not found"})

        return Response(status_code=201)