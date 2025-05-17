from src.core import UnitOfWork, DbHealthReader, MetricConfigurationLoader, GenericDataSeeder, LayoutItemLoader, \
    MetricConfiguration, LayoutItem, QueryLoader, Query
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
class DataSeedService:

    def __init__(self,
        unit_of_work: UnitOfWork,
        metrics_loader: MetricConfigurationLoader,
        layouts_loader: LayoutItemLoader,
        query_loader: QueryLoader,
        logger: Logger
    ):
        self.logger = logger
        self.query_loader = query_loader
        self.layouts_loader = layouts_loader
        self.metric_configs_loader = metrics_loader
        self.unit_of_work = unit_of_work

    async def __call__(self) -> bool:
        metric_configs = await self.metric_configs_loader()
        layout_items = await self.layouts_loader()
        queries = await self.query_loader()
        async with self.unit_of_work as uow:
            seed = uow.persistence_factory(GenericDataSeeder)
            await seed(data=metric_configs, _type=MetricConfiguration, logger=self.logger)
            await seed(data=layout_items, _type=LayoutItem, logger=self.logger)
            await seed(data=queries, _type=Query, logger=self.logger)
            await uow.commit()
        return False