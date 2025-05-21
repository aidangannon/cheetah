import asyncio
import logging
import os
import threading
import uuid
from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from punq import Container, Scope
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.testclient import TestClient
from structlog.contextvars import get_contextvars

from src.application.services import DataSeedService
from src.bootstrap import bootstrap
from src.crosscutting import Logger
from src.infrastructure import Settings

def step(func):
    """
    decorator for scenario steps
    """
    def wrapper(self, *args, **kwargs):
        try:
            print(f"{func.__name__}")
            result = func(self, *args, **kwargs)
            print(f"STEP PASS")
            return result
        except AssertionError as e:
            print(f"STEP FAILED")
            self.runner.failures.append((func.__name__, e))
        except Exception as e:
            print(f"STEP EXCEPTION")
            self.runner.failures.append((func.__name__, e))
        return self
    return wrapper

def seed_db(app: FastAPI):
    seed_service = app.state.services[DataSeedService]
    asyncio.run(seed_service())


class ScenarioRunner:

    def __init__(self):
        self.failures = []

    def assert_all(self):
        """
        enables tdd via final assertion
        """

        if self.failures:
            msgs = [f"Step {name} failed: {ex}" for name, ex in self.failures]
            raise AssertionError("\n".join(msgs))


class FastApiTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_logger = TestLogger()
        cls.setup_db()
        app = FastAPI()
        settings = Settings(
            QUERIES_SEED_CSV="./data/sqlite_compliant_queries.csv",
            METRICS_SEED_JSON = "./data/metrics.json",
            METRIC_RECORDS_SEED_JSON="./data/metric_records.json"
        )

        def override_deps(populated_container: Container):
            populated_container.register(Logger, instance=cls.test_logger)
            populated_container.register(Settings, instance=settings, scope=Scope.singleton)

        bootstrap(app, initialise_actions=override_deps, use_env_settings=False)

        seed_db(app=app)

        cls.client = TestClient(app)

    @classmethod
    def setup_db(cls):
        cls.db_engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.engine_patcher = patch("sqlalchemy.ext.asyncio.create_async_engine")
        engine = cls.engine_patcher.start()
        engine.return_value = cls.db_engine
        alembic_cfg = Config("./alembic.ini")
        command.upgrade(alembic_cfg, "head")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine_patcher.stop()
        asyncio.run(cls.db_engine.dispose())

    def assert_there_is_log_with(self, test_logger, log_level, message: str, scoped_vars: dict = None):
        logs_with_log_level = [log for log in test_logger.logs if log[0] == log_level]
        logs_with_message = [log for log in logs_with_log_level if log[1] == message]
        if scoped_vars is None:
            scoped_vars = {}

        # Convert scoped_vars items to a list to preserve order
        scoped_items = list(scoped_vars.items())

        logs_with_scoped_values = [
            log for log in logs_with_message
            if dict(list(log[3].items())) == dict(scoped_items)  # exact same order and content
        ]
        self.assertEqual(len(logs_with_scoped_values), 1)


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
        print(f"{logging.getLevelName(level)} {msg} ARGS: {args} KWARGS: {kwargs}")
        context_data = get_contextvars()
        combined_data = {**context_data, **kwargs}  # kwargs take precedence
        self.append((level, msg, args, combined_data))

    @property
    def logs(self) -> list:
        return self.get_all()


@dataclass
class ScenarioContext:
    client: TestClient
    test_case: FastApiTestCase
    logger: Logger
    runner: ScenarioRunner