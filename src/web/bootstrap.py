import logging
import sys
from typing import Callable

import structlog
from fastapi import FastAPI
from punq import Container

from src.crosscutting import Logger, ServiceProvider
from src.web.routes import router


def bootstrap(app: FastAPI, initialise_actions: Callable[[Container], None] = lambda x: None):
    """
    sets up the app, spins up ioc, adds logging, adds app settings
    :param app: flask application for building
    :param initialise_actions: optional actions to override any dependencies
    """
    container = Container()
    add_logging(container=container)
    add_routing(app=app, container=container)
    initialise_actions(container)
    return container

def add_routing(app: FastAPI, container: Container):
    app.state.services = ServiceProvider(container=container)
    app.include_router(router=router)

def add_logging(container: Container):
    container.register(Logger, factory=structlog.getLogger)
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
            structlog.processors.JSONRenderer(indent=2)
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),

        cache_logger_on_first_use=True,
    )