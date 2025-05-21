from datetime import date
from typing import Optional

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core import MetricConfigurationAggregate, MetricRecord
from src.crosscutting import auto_slots


@auto_slots
class SqlAlchemyDbHealthReader:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self) -> Optional[int]:
        result = await self.session.execute(text("SELECT 1"))
        row = result.fetchone()
        return row


@auto_slots
class SqlAlchemyMetricAggregateReader:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, _id: str) -> Optional[MetricConfigurationAggregate]:
        result = await self.session.execute(
            select(MetricConfigurationAggregate).where(MetricConfigurationAggregate.id == _id).options(
                selectinload(MetricConfigurationAggregate.layouts),
                selectinload(MetricConfigurationAggregate.query),
            )
        )
        return result.scalar_one_or_none()

@auto_slots
class SqlAlchemyMetricRecordsReader:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, query: str, start_date: date, end_date: date, day_range: int) -> list[dict]:
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "day_range": day_range,
        }
        result = await self.session.execute(text(query), params)
        rows = result.mappings().all()
        return [dict(row) for row in rows]