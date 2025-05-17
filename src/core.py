from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, TypeVar, Type, Optional

T = TypeVar("T")


class UnitOfWork(Protocol):

    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(self, exc_type, exc_value, traceback):
        ...

    def persistence_factory(self, cls: Type[T]) -> T:
        ...

    async def commit(self):
        ...

class DbHealthReader(Protocol):

    async def __call__(self) -> Optional[int]:
        ...

@dataclass(unsafe_hash=True, slots=True)
class MetricRecord:
    metric_id: str = None
    id: str = None # query id
    date: datetime = None
    obsolescence_val: float = None
    parts_flagged: int = None
    alert_type: str = None
    alert_category: str = None


@dataclass(unsafe_hash=True, slots=True)
class MetricConfiguration:
    id: str = None
    queryId: str = None
    isEditable: bool = None


@dataclass(unsafe_hash=True, slots=True)
class LayoutItem:
    id: str = None
    item_id: str = None
    breakpoint: str = None
    x: int = None
    y: int = None
    w: int = None
    h: int = None
    static: bool = None


@dataclass(unsafe_hash=True, slots=True)
class Query:
    id: str = None
    query: str = None