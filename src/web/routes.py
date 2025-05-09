from fastapi import APIRouter, Depends

from src.crosscutting import get_service, logging_scope, Logger

router = APIRouter()

async def get_health(logger = Depends(get_service(Logger))):
    with logging_scope(operation=get_health.__name__):
        logger.info("Endpoint called", fay=2)
        return {"status": "running"}

router.add_api_route(path="/health", methods=["GET"], endpoint=get_health)