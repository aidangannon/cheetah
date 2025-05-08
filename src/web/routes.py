from fastapi import APIRouter, Depends

from src.crosscutting import get_service, logging_scope, Logger

router = APIRouter()

async def root(logger = Depends(get_service(Logger))):
    with logging_scope(operation="My stuff"):
        logger.info(f"My stuff", fay=2)
        return {"message": "Customer API", "status": "running"}

router.add_api_route(path="/", methods=["GET"], endpoint=root)