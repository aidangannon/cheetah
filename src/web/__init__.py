from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.crosscutting import Logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.services[Logger].info("Starting service")

    yield

    app.state.services[Logger].info("Shutting down service")


