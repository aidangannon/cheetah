from src.core import UnitOfWork, HealthReader
from src.crosscutting import auto_slots


@auto_slots
class HealthCheckService:

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self) -> bool:
        async with self.unit_of_work as uow:
            health_reader = uow.persistence_factory(HealthReader)
            row = await health_reader()

            if row is None:
                return False

            return True