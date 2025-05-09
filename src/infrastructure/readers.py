from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.crosscutting import auto_slots


@auto_slots
class SqlAlchemyHealthReader:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self) -> Optional[int]:
        result = await self.session.execute(text("SELECT 1"))
        row = result.fetchone()
        return row