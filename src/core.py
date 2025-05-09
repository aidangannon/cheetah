from typing import Protocol, TypeVar, Type

T = TypeVar("T")


class UnitOfWork(Protocol):

    async def __aenter__(self) -> "UnitOfWork":
        ...

    async def __aexit__(self, exc_type, exc_value, traceback):
        ...

    def repository_factory(self, repo_cls: Type[T]) -> T:
        ...

    async def commit(self):
        ...