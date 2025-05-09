import inspect
from contextlib import contextmanager
from typing import Callable, TypeVar, Any, Protocol
from fastapi import Request, Depends
from punq import Container

from structlog.contextvars import bind_contextvars, clear_contextvars

T = TypeVar("T")

class Logger(Protocol):
    """
    non-implementation specific duck-type for the logger
    """
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

@contextmanager
def logging_scope(**context):
    """
    :param context: scoped logging variables for application indexing
    """
    bind_contextvars(**context)
    try:
        yield
    finally:
        clear_contextvars()


def get_service(service_type: Callable[..., T]) -> Callable[[Request], T]:
    """
    gets a type from the service registry
    """
    def _get(request: Request) -> T:
        print(service_type)
        services = request.app.state.services
        return services[service_type]
    return _get


def auto_slots(cls):
    """
    defines a class with slots to reduce method invocation time and memory overhead of services
    """

    # Get parameter names of __init__
    params = inspect.signature(cls.__init__).parameters

    # set __slots__ to these attribute names excluding self
    cls.__slots__ = tuple([name for name in params if name != "self"])
    return cls


@auto_slots
class ServiceProvider:
    """
    dictionary registry of services, layer of indirection between application and container
    """
    def __init__(self, container: Container):
        self.container = container

    def __getitem__(self, key):
        return self.container.resolve(key)