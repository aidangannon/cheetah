from src.core import UnitOfWork, DbHealthReader
from src.crosscutting import auto_slots


@auto_slots
class DatabaseHealthCheckService:

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self) -> bool:
        async with self.unit_of_work as uow:
            health_reader = uow.persistence_factory(DbHealthReader)
            row = await health_reader()

            if row is None:
                return False

            return True