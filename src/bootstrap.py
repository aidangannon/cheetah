from typing import Callable

import structlog
from punq import Container
from structlog import BoundLogger

def bootstrap(initialise_actions: Callable[[Container], None]):
    """
    sets up the app, spins up ioc, adds logging, adds app settings
    :param initialise_actions: optional actions to override any dependencies
    """

    container = Container()
    container.register(BoundLogger, factory=structlog.getLogger)
    initialise_actions(container)