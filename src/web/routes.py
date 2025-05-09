from fastapi import APIRouter, Depends

from src.application import HealthCheckService
from src.crosscutting import get_service, logging_scope, Logger

router = APIRouter()

async def get_health(
    logger: Logger = Depends(get_service(Logger)),
    health_check_service: HealthCheckService = Depends(get_service(HealthCheckService))
):
    with logging_scope(operation=get_health.__name__):
        logger.info("Endpoint called")
        database_result = await health_check_service()
        return {"application": True, "database": database_result}

router.add_api_route(path="/health", methods=["GET"], endpoint=get_health)