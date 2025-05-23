import asyncio
import uuid
from datetime import date
from typing import Optional

from src.core import UnitOfWork, DbHealthReader, GenericDataSeeder, DataLoader, MetricConfigurationAggregate, \
    MetricAggregateReader, MetricRecordsReader, MetricAggregateWriter, QueryGenerator, Query, MetricRecord, \
    MetricRecordWriter
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

    async def __call__(self, _id: str, start_date: date, end_date: date, day_range: int) -> Optional[MetricConfigurationAggregate]:
        async with self.unit_of_work as uow:
            config_reader = uow.persistence_factory(MetricAggregateReader)
            records_reader = uow.persistence_factory(MetricRecordsReader)
            metrics_config = await config_reader(_id=_id)
            if metrics_config is None:
                return None
            records = await records_reader(
                query=metrics_config.query.query,
                start_date=start_date,
                end_date=end_date,
                day_range=day_range
            )
        metrics_config.records = records
        return metrics_config


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
            await uow.save()


@auto_slots
class CreateMetricConfigurationService:

    def __init__(self,
        unit_of_work: UnitOfWork,
        prompt_generator: QueryGenerator
    ):
        self.prompt_generator = prompt_generator
        self.unit_of_work = unit_of_work

    async def __call__(self, aggregate: MetricConfigurationAggregate, query_prompt: str) -> str:
        async with self.unit_of_work as uow:
            query_id = str(uuid.uuid4())
            query = await self.prompt_generator(query_prompt, _q=query_id)
            aggregate.query = Query(
                id=query_id,
                query=query
            )
            writer = uow.persistence_factory(MetricAggregateWriter)
            await writer(aggregate)
            await uow.save()
        return aggregate.id


@auto_slots
class CreateMetricService:

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, config_id: str, metric_record: MetricRecord) -> Optional[str]:
        async with self.unit_of_work as uow:
            reader = uow.persistence_factory(MetricAggregateReader)
            aggregate = await reader(config_id)

            if aggregate is None:
                return None

            metric_record.id = aggregate.query_id
            writer = uow.persistence_factory(MetricRecordWriter)
            await writer(metric_record)
            await uow.save()
        return aggregate.id