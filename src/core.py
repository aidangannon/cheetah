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