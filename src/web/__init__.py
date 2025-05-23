from contextlib import asynccontextmanager
from typing import Protocol, Any, Coroutine, Callable

from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request

from src.application.services import DataSeedService
from src.crosscutting import Logger, ServiceProvider


security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    provider: ServiceProvider = app.state.services
    provider[Logger].info("Starting service")
    seed_service = provider[DataSeedService]
    await seed_service()

    yield

    provider[Logger].info("Shutting down service")


class Authenticator(Protocol):

    async def __call__(self, credentials: HTTPAuthorizationCredentials) -> dict:
        ...

def get_authenticator_from_services(request: Request) -> Authenticator:
    authenticator = request.app.state.services[Authenticator]
    return authenticator

async def auth_provider(
    authenticator: Authenticator = Depends(get_authenticator_from_services),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    auth_call = authenticator(credentials)
    return await auth_call