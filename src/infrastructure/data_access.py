from datetime import date
from typing import Optional

from sqlalchemy import text, select, exists, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core import DatasetConfigAggregate, DataPoint, DatasetConfig
from src.crosscutting import auto_slots, Logger, logging_scope
from src.infrastructure import async_ttl_cache


@auto_slots
class SqlAlchemyDbHealthReader:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self) -> Optional[int]:
        result = await self.session.execute(text("SELECT 1"))
        row = result.fetchone()
        return row


@auto_slots
class DatasetRetriever:

    def __init__(self, session: AsyncSession, logger: Logger):
        self.logger = logger
        self.session = session

    @async_ttl_cache(ttl_seconds=300)
    async def __call__(self, _id: str) -> Optional[DatasetConfigAggregate]:
        result = await self.session.execute(
            select(DatasetConfigAggregate).where(DatasetConfigAggregate.id == _id).options(
                selectinload(DatasetConfigAggregate.layouts),
                selectinload(DatasetConfigAggregate.statement),
            )
        )
        self.logger.info(f"Retrieving dataset configurations for from db", dataset_configuration_id=_id)
        return result.scalar_one_or_none()

@auto_slots
class SqlAlchemyDataPointReader:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, statement: str, start_date: date, end_date: date, day_range: int) -> list[dict]:
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "day_range": day_range,
        }
        result = await self.session.execute(text(statement), params)
        rows = result.mappings().all()
        return [dict(row) for row in rows]


@auto_slots
class DatabaseBootstrapper:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, data: list, _type, logger: Logger) -> None:
        """
        seeds the table if the table is not already empty
        """
        with logging_scope(operation="db_seed"):
            logger.info(f"{len(data)} input rows")
            stmt = select(func.count()).select_from(_type.__table__)

            result = await self.session.execute(stmt)
            count = result.scalar()

            logger.info(f"{count} rows found in db")
            if count > 0:
                return

            self.session.add_all(data)


@auto_slots
class SqlAlchemyDatasetAggregateWriter:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, aggregate: DatasetConfigAggregate):
        self.session.add(aggregate)


@auto_slots
class SqlAlchemyDataPointWriter:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, record: DataPoint):
        self.session.add(record)