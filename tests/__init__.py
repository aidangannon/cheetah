import logging
import threading

from fastapi import FastAPI
from punq import Container, Scope
from starlette.testclient import TestClient
from structlog.contextvars import get_contextvars

from src.crosscutting import Logger
from src.bootstrap import bootstrap
from src.infrastructure import Settings


def step(func):
    """
    decorator for scenario steps
    """
    def wrapper(self, *args, **kwargs):
        try:
            print(f"\n{func.__name__}")
            return func(self, *args, **kwargs)
        except AssertionError as e:
            print(f"STEP FAILED")
            self.runner.failures.append((func.__name__, e))
        except Exception as e:
            print(f"STEP EXCEPTION")
            self.runner.failures.append((func.__name__, e))
        return self
    return wrapper


def assert_there_is_log_with(test_logger, log_level, message: str, scoped_vars: dict):
    logs_with_log_level = [log for log in test_logger.logs if log[0] == log_level]
    logs_with_message = [log for log in logs_with_log_level if log[1] == message]
    logs_with_scoped_values = [
        log for log in logs_with_message
        if all(item in log[3].items() for item in scoped_vars.items())
    ]
    assert len(logs_with_scoped_values) == 1, f"Expected exactly one log matching criteria, found {len(logs_with_scoped_values)}"


class FastApiScenarioRunner:
    __slots__ = ("test_logger", "failures", "client")

    def __init__(self) -> None:
        self.test_logger = TestLogger()
        self.failures = []
        app = FastAPI()
        settings = Settings(DATABASE_URL="sqlite+aiosqlite:///:memory:")

        def override_deps(populated_container: Container):
            populated_container.register(Logger, instance=self.test_logger)
            populated_container.register(Settings, instance=settings, scope=Scope.singleton)

        bootstrap(app, initialise_actions=override_deps, use_env_settings=False)
        self.client = TestClient(app)

    def assert_all(self):
        """
        enables tdd via final assertion
        """

        if self.failures:
            msgs = [f"Step {name} failed: {ex}" for name, ex in self.failures]
            raise AssertionError("\n".join(msgs))


def make_thread_safe_list():
    """
    closure over a thread-safe list with lock
    """

    _list = []
    _lock = threading.Lock()

    def append(item):
        with _lock:
            _list.append(item)

    def get_all():
        with _lock:
            return list(_list)

    return append, get_all


class TestLogger:
    __slots__ = ("append", "get_all")

    def __init__(self):
        append, get_all = make_thread_safe_list()
        self.append = append
        self.get_all = get_all

    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, msg, args, kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, msg, args, kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, args, kwargs)

    def _log(self, level, msg, *args, **kwargs):
        # merge custom kwargs with contextvars
        context_data = get_contextvars()
        combined_data = {**context_data, **kwargs}  # kwargs take precedence
        self.append((level, msg, args, combined_data))

    @property
    def logs(self) -> list:
        return self.get_all()