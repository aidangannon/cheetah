import asyncio
from typing import Optional

from src.core import UnitOfWork, DbHealthReader, GenericDataSeeder, DataLoader, MetricConfigurationAggregate, \
    MetricAggregateReader
from src.crosscutting import auto_slots, Logger


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


@auto_slots
class GetMetricsService:

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, _id: str) -> Optional[MetricConfigurationAggregate]:
        async with self.unit_of_work as uow:
            config_reader = uow.persistence_factory(MetricAggregateReader)
            result = await config_reader(_id=_id)
            print("")


@auto_slots
class DataSeedService:

    def __init__(self,
        unit_of_work: UnitOfWork,
        loaders: list[DataLoader],
        logger: Logger
    ):
        self.loaders = loaders
        self.logger = logger
        self.unit_of_work = unit_of_work

    async def __call__(self):
        await asyncio.gather(*(loader() for loader in self.loaders))
        async with self.unit_of_work as uow:
            seed = uow.persistence_factory(GenericDataSeeder)
            for loader in self.loaders:
                await seed(data=loader.data, _type=loader.type, logger=self.logger)
            await uow.commit()