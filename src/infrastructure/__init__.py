import time
from functools import wraps
from typing import TypeVar, Type, Any, Callable, Coroutine, Optional

import sqlalchemy
from pydantic.v1 import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from src.crosscutting import Logger

Base = declarative_base()


PERSISTENCE_REGISTRY = {}

def register(interface: Type, implementation: Type):
    PERSISTENCE_REGISTRY[interface] = implementation


T = TypeVar("T")


class Settings(BaseSettings):
    DATABASE_URL: str
    METRICS_SEED_JSON: str = "../data/metrics.json"
    QUERIES_SEED_CSV: str = "../data/queries.csv"
    METRIC_RECORDS_SEED_JSON: str = "../data/metric_records.json"

    class Config:
        env_file = "../.env.local"

class SqlAlchemyUnitOfWork:
    __slots__ = "session_factory", "logger", "session"

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        engine = sqlalchemy.ext.asyncio.create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True,
        )
        self.session_factory = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def __aenter__(self):
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self.session.rollback()
        finally:
            await self.session.close()

    def persistence_factory(self, cls: Type[T]) -> T:
        """
        Slightly expensive to new up repo each time,
        also requires each repo to have only 1 or 2 arguments:
        - session (mandatory)
        - logger (optional)
        """

        repo_cls = PERSISTENCE_REGISTRY[cls]
        params = repo_cls.__init__.__annotations__

        if 'logger' in params:
            return repo_cls(self.session, logger=self.logger)
        else:
            return repo_cls(self.session)

    async def commit(self):
        await self.session.commit()


def async_ttl_cache(ttl_seconds: int = 300):
    cache = {}

    def decorator(func: Callable[..., Coroutine[Any, Any, Optional[Any]]]):
        @wraps(func)
        async def wrapper(self, _id: str, *args, **kwargs) -> Optional[Any]:
            now = time.time()
            logger: Logger = self.logger
            if _id in cache:
                cached_time, cached_value = cache[_id]
                if now - cached_time < ttl_seconds:
                    logger.info("Cache hit", cache_id=_id)
                    return cached_value
                else:
                    logger.info("Cache expired", cache_id=_id)
                    del cache[_id]
            logger.info("Cache miss", cache_id=_id)
            result = await func(self, _id, *args, **kwargs)
            cache[_id] = (now, result)
            return result
        return wrapper
    return decorator