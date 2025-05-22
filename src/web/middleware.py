from typing import Callable

from fastapi import FastAPI
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


def log_and_handle(
    status_code: int,
    message: str,
    logger_factory: Callable[[], Logger]
) -> HTTPExceptionHandler:

    def handler(_: Request, exc: Exception) -> JSONResponse:
        logger = logger_factory()
        logger.error("Error occurred", exc_info=exc, exec_str=str(exc))

        content = {"error": message}

        return JSONResponse(status_code=status_code, content=content)

    return handler