from contextlib import contextmanager

from structlog.contextvars import bind_contextvars, clear_contextvars


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