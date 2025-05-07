import logging
from typing import Callable

import structlog
from punq import Container
from structlog import BoundLogger
import sys

def bootstrap(initialise_actions: Callable[[Container], None] = lambda x: None) -> Container:
    """
    sets up the app, spins up ioc, adds logging, adds app settings
    :param initialise_actions: optional actions to override any dependencies
    """
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
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.JSONRenderer(indent=2)
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),

        cache_logger_on_first_use=True,
    )

    container = Container()
    container.register(BoundLogger, factory=structlog.getLogger)
    initialise_actions(container)
    return container