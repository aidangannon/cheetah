from typing import Callable

from fastapi import FastAPI
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import HTTPExceptionHandler

from src.crosscutting import Logger


def add_exception_middleware(app: FastAPI):
    logger_factory = lambda: app.state.services[Logger]

    app.add_exception_handler(
        Exception,
        log_and_handle(
            status_code=500,
            message="Internal server error",
            logger_factory=logger_factory
        )
    )

    app.add_exception_handler(
        RequestValidationError,
        log_and_forward_validation_error(logger_factory)
    )


def log_and_handle(
    status_code: int,
    message: str,
    logger_factory: Callable[[], Logger]
) -> Callable[[Request, Exception], JSONResponse]:

    def handler(_: Request, exc: Exception) -> JSONResponse:
        logger = logger_factory()
        logger.error("Unhandled exception", exc_info=exc, extra={"error_str": str(exc)})
        content = {"error": message}
        return JSONResponse(status_code=status_code, content=content)

    return handler


def log_and_forward_validation_error(
    logger_factory: Callable[[], Logger]
) -> Callable[[Request, RequestValidationError], JSONResponse]:

    async def handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger = logger_factory()
        logger.warning("Validation error", exc_info=exc, extra={"error_str": str(exc)})
        return await request_validation_exception_handler(request, exc)

    return handler