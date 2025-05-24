import datetime
from dataclasses import dataclass, field
from typing import Protocol, TypeVar, Type, Optional, Any

from src.crosscutting import Logger

T = TypeVar("T")


@dataclass(unsafe_hash=True)
class DataPoint:
    dataset_id: str = None
    id: str = None # statement id
    timestamp: datetime.datetime = None
    decay_value: float = None
    decay_rate: float = None
    items_flagged: int = None
    notification_type: str = None
    notification_category: str = None

@dataclass(unsafe_hash=True)
class ViewConfig:
    id: str = None
    element_id: str = None
    breakpoint: str = None
    x: int = None
    y: int = None
    w: int = None
    h: int = None
    static: bool = None

@dataclass(unsafe_hash=True)
class SqlStatement:
    id: str = None
    statement: str = None

@dataclass(unsafe_hash=True)
class DatasetConfig:
    """
    used for writing in a stateless fashion
    """
    id: str = None
    statement_id: str = None
    is_mutable: bool = None


@dataclass(unsafe_hash=True)
class DatasetConfigAggregate(DatasetConfig):
    """
    used for querying with related models attached
    """
    layouts: list[ViewConfig] = field(default_factory=list)
    statement: SqlStatement = None
    records: list[dict] = field(default_factory=list)


class DbHealthReader(Protocol):

    async def __call__(self) -> Optional[int]:
        ...


class DatasetAggregateReader(Protocol):

    async def __call__(self, _id: str) -> Optional[DatasetConfigAggregate]:
        ...


class DataPointReader(Protocol):

    async def __call__(self, statement: str, start_date: datetime.date, end_date: datetime.date, day_range: int) -> list[dict]:
        ...


class UnitOfWork(Protocol):

    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(self, exc_type, exc_value, traceback):
        ...

    def persistence_factory(self, cls: Type[T]) -> T:
        ...

    async def save(self):
        ...

class DataLoader(Protocol):
    type: type
    data: list[Any]
    logger: Logger

    async def __call__(self) -> None:
        ...

class GenericDataSeeder(Protocol):

    async def __call__(self, data: list, _type, logger: Logger) -> None:
        ...

class DatasetAggregateWriter(Protocol):

    async def __call__(self, aggregate: DatasetConfigAggregate):
        ...


class StatementGenerator(Protocol):

    async def __call__(self, prompt: str, _q: str) -> str:
        ...

class DataPointWriter(Protocol):

    async def __call__(self, record: DataPoint):
        ...