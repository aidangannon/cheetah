import logging
import sys
from typing import Callable

import structlog
import watchtower
from dotenv import load_dotenv
from fastapi import FastAPI
from punq import Container, Scope

from src.application import DatabaseHealthCheckService
from src.core import UnitOfWork, DbHealthReader
from src.crosscutting import Logger, ServiceProvider
from src.infrastructure import Settings, SqlAlchemyUnitOfWork, register, SqlAlchemyDbHealthReader
from src.web.routes import health_router


def bootstrap(app: FastAPI, initialise_actions: Callable[[Container], None] = lambda x: None):
    """
    sets up the app, spins up ioc, adds logging, adds app settings
    :param app: flask application for building
    :param initialise_actions: optional actions to override any dependencies
    """
    container = Container()
    add_logging(container=container)
    add_configuration(container=container)
    add_routing(app=app, container=container)
    add_database(container=container)
    add_services(container=container)
    initialise_actions(container)
    return container

def add_database(container: Container):
    register(DbHealthReader, SqlAlchemyDbHealthReader)
    container.register(UnitOfWork, SqlAlchemyUnitOfWork)

def add_configuration(container: Container):
    container.register(Settings, instance=Settings(), scope=Scope.singleton)

def add_routing(app: FastAPI, container: Container):
    app.state.services = ServiceProvider(container=container)
    app.include_router(router=health_router)

def add_services(container: Container):
    container.register(DatabaseHealthCheckService)

def add_logging(container: Container):
    cloudwatch_handler = watchtower.CloudWatchLogHandler(
        log_group="/my-app/fastapi",
        stream_name="intropy-metrics"
    )
    console_handler = logging.StreamHandler(sys.stdout)
    container.register(Logger, factory=structlog.getLogger, scope=Scope.singleton)
    logging.basicConfig(
        format="%(message)s",
        handlers=[cloudwatch_handler, console_handler],
        level=logging.INFO,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.JSONRenderer(indent=2)
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),

        cache_logger_on_first_use=True,
    )