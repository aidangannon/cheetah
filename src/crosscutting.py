import inspect
from contextlib import contextmanager
from functools import wraps
from typing import Optional

from fastapi import Depends
from punq import Container
from structlog.contextvars import bind_contextvars, clear_contextvars

_container: Optional[Container] = None

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

def set_container(container):
    global _container
    _container = container

def inject(dep_type):
    return Depends(lambda: _container.resolve(dep_type))