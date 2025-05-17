from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, TypeVar, Type, Optional

from src.crosscutting import Logger

T = TypeVar("T")


@dataclass(unsafe_hash=True)
class MetricRecord:
    metric_id: str = None
    id: str = None # query id
    date: datetime = None
    obsolescence_val: float = None
    parts_flagged: int = None
    alert_type: str = None
    alert_category: str = None

@dataclass(unsafe_hash=True)
class LayoutItem:
    id: str = None
    item_id: str = None
    breakpoint: str = None
    x: int = None
    y: int = None
    w: int = None
    h: int = None
    static: bool = None

@dataclass(unsafe_hash=True)
class Query:
    id: str = None
    query: str = None

@dataclass(unsafe_hash=True)
class MetricConfiguration:
    """
    used for writing in a stateless fashion
    """
    id: str = None
    query_id: str = None
    is_editable: bool = None


@dataclass(unsafe_hash=True)
class MetricConfigurationAggregate(MetricConfiguration):
    """
    used for querying with related models attached
    """
    layouts: list[LayoutItem] = field(default_factory=list)
    query: Query = None


class DbHealthReader(Protocol):

    async def __call__(self) -> Optional[int]:
        ...


class UnitOfWork(Protocol):

    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(self, exc_type, exc_value, traceback):
        ...

    def persistence_factory(self, cls: Type[T]) -> T:
        ...

    async def commit(self):
        ...


class MetricConfigurationLoader(Protocol):

    async def __call__(self) -> list[MetricConfiguration]:
        ...

class LayoutItemLoader(Protocol):

    async def __call__(self) -> list[LayoutItem]:
        ...

class QueryLoader(Protocol):

    async def __call__(self) -> list[LayoutItem]:
        ...

class GenericDataSeeder(Protocol):

    async def __call__(self, data: list, _type, logger: Logger) -> None:
        ...