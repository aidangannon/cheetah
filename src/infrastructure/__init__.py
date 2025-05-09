from typing import TypeVar, Type

from pydantic.v1 import BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from src.infrastructure.readers import SqlAlchemyDbHealthReader

Base = declarative_base()


PERSISTENCE_REGISTRY = {}

def register(interface: Type, implementation: Type):
    PERSISTENCE_REGISTRY[interface] = implementation


T = TypeVar("T")


class Settings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8"
    )

class SqlAlchemyUnitOfWork:

    def __init__(self, settings: Settings):
        engine = create_async_engine(
            settings.database_url,
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
        todo: slightly expensive to new up repo each time, also requires each repo to have only 1 argument of session
        """
        return PERSISTENCE_REGISTRY[cls](self.session)

    async def commit(self):
        await self.session.commit()
