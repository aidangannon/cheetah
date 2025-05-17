from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.application.services import DataSeedService
from src.crosscutting import Logger, ServiceProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    provider: ServiceProvider = app.state.services
    provider[Logger].info("Starting service")
    seed_service = provider[DataSeedService]
    await seed_service()

    yield

    provider[Logger].info("Shutting down service")


