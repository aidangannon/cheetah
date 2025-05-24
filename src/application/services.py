import asyncio
import uuid
from datetime import date
from typing import Optional

from src.core import UnitOfWork, DbHealthReader, GenericDataSeeder, DataLoader, DatasetConfigAggregate, \
    DatasetAggregateReader, DataPointReader, DatasetAggregateWriter, StatementGenerator, SqlStatement, DataPoint, \
    DataPointWriter
from src.crosscutting import auto_slots, Logger


@auto_slots
class SystemStatusChecker:

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
class DataRetrievalHandler:

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, _id: str, start_date: date, end_date: date, day_range: int) -> Optional[DatasetConfigAggregate]:
        async with self.unit_of_work as uow:
            config_reader = uow.persistence_factory(DatasetAggregateReader)
            records_reader = uow.persistence_factory(DataPointReader)
            dataset_config = await config_reader(_id=_id)
            if dataset_config is None:
                return None
            records = await records_reader(
                statement=dataset_config.statement.statement,
                start_date=start_date,
                end_date=end_date,
                day_range=day_range
            )
        dataset_config.records = records
        return dataset_config


@auto_slots
class DataBootstrapper:

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
            await uow.save()


@auto_slots
class ConfigurationManager:

    def __init__(self,
        unit_of_work: UnitOfWork,
        prompt_generator: StatementGenerator
    ):
        self.prompt_generator = prompt_generator
        self.unit_of_work = unit_of_work

    async def __call__(self, aggregate: DatasetConfigAggregate, statement_prompt: str) -> str:
        async with self.unit_of_work as uow:
            statement_id = str(uuid.uuid4())
            statement = await self.prompt_generator(statement_prompt, _q=statement_id)
            aggregate.statement = SqlStatement(
                id=statement_id,
                statement=statement
            )
            writer = uow.persistence_factory(DatasetAggregateWriter)
            await writer(aggregate)
            await uow.save()
        return aggregate.id


@auto_slots
class DataPointCreationService:

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, config_id: str, data_point: DataPoint) -> Optional[str]:
        async with self.unit_of_work as uow:
            reader = uow.persistence_factory(DatasetAggregateReader)
            aggregate = await reader(config_id)

            if aggregate is None:
                return None

            data_point.id = aggregate.statement_id
            writer = uow.persistence_factory(DataPointWriter)
            await writer(data_point)
            await uow.save()
        return aggregate.id