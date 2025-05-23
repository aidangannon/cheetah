import logging
import sys
from typing import Callable

import structlog
from fastapi import FastAPI
from punq import Container, Scope

from src.application.services import DatabaseHealthCheckService, DataSeedService, GetMetricsService, \
    CreateMetricConfigurationService, CreateMetricService
from src.core import UnitOfWork, DbHealthReader, DataLoader, GenericDataSeeder, MetricAggregateReader, \
    MetricRecordsReader, MetricAggregateWriter, MetricRecordWriter, QueryGenerator
from src.crosscutting import Logger, ServiceProvider
from src.infrastructure import Settings, SqlAlchemyUnitOfWork, register
from src.infrastructure.auth import CognitoAuthenticator
from src.infrastructure.llm import FakeQueryGenerator
from src.infrastructure.loaders import JsonMetricConfigurationLoader, JsonLayoutItemLoader, CsvQueryLoader, \
    JsonMetricRecordLoader
from src.infrastructure.orm import start_mappers
from src.infrastructure.readers import SqlAlchemyMetricAggregateReader, SqlAlchemyMetricRecordsReader, \
    SqlAlchemyDbHealthReader
from src.infrastructure.writers import SqlAlchemyGenericDataSeeder, SqlAlchemyMetricAggregateWriter, \
    SqlAlchemyMetricRecordWriter
from src.web import Authenticator
from src.web.middleware import add_exception_middleware
from src.web.routes import health_router, metrics_router


def bootstrap(app: FastAPI,
    initialise_actions: Callable[[Container], None] = lambda x: None,
    use_env_settings: bool = True
):
    """
    sets up the app, spins up ioc, adds logging, adds app settings
    :param app: flask application for building
    :param initialise_actions: optional actions to override any dependencies
    """
    container = Container()
    add_logging(container=container)
    if use_env_settings:
        add_configuration(container=container)
    add_routing(app=app, container=container)
    add_exception_middleware(app=app)
    add_database(container=container)
    add_services(container=container)
    add_loaders(container=container)
    add_llms(container=container)
    add_auth(container=container)
    initialise_actions(container)
    return container

def add_database(container: Container):
    start_mappers()
    register(DbHealthReader, SqlAlchemyDbHealthReader)
    register(MetricRecordsReader, SqlAlchemyMetricRecordsReader)
    register(MetricAggregateReader, SqlAlchemyMetricAggregateReader)
    register(GenericDataSeeder, SqlAlchemyGenericDataSeeder)
    register(MetricAggregateWriter, SqlAlchemyMetricAggregateWriter)
    register(MetricRecordWriter, SqlAlchemyMetricRecordWriter)
    container.register(UnitOfWork, SqlAlchemyUnitOfWork)

def add_llms(container: Container):
    container.register(QueryGenerator, FakeQueryGenerator)

def add_auth(container: Container):
    container.register(Authenticator, CognitoAuthenticator)

def add_loaders(container: Container):
    container.register(DataLoader, JsonMetricConfigurationLoader)
    container.register(DataLoader, JsonLayoutItemLoader)
    container.register(DataLoader, JsonMetricRecordLoader)
    container.register(DataLoader, CsvQueryLoader)

def add_configuration(container: Container):
    container.register(Settings, instance=Settings(), scope=Scope.singleton)

def add_routing(app: FastAPI, container: Container):
    app.state.services = ServiceProvider(container=container)
    app.include_router(router=health_router)
    app.include_router(router=metrics_router)

def add_services(container: Container):
    container.register(DatabaseHealthCheckService)
    container.register(GetMetricsService)
    container.register(DataSeedService)
    container.register(CreateMetricConfigurationService)
    container.register(CreateMetricService)

def add_logging(container: Container):
    container.register(Logger, factory=structlog.getLogger, scope=Scope.singleton)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,  # or DEBUG
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),

        cache_logger_on_first_use=True,
    )