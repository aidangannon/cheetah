from sqlalchemy import exists, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import MetricConfiguration
from src.crosscutting import auto_slots, Logger, logging_scope


@auto_slots
class SqlAlchemyGenericDataSeeder:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, data: list, _type, logger: Logger) -> None:
        """
        seeds the table if the table is not already empty
        """
        with logging_scope({"operation": "db_seed"}):
            logger.info(f"{len(data)} input rows")
            stmt = select(func.count()).select_from(_type.__table__)

            result = await self.session.execute(stmt)
            count = result.scalar()

            logger.info(f"{count} rows found in db")
            if count > 0:
                return

            self.session.add_all(data)