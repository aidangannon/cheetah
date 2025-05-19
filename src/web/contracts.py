from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic.v1 import BaseModel, validator


class LayoutItemResponse(BaseModel):
    id: str
    item_id: str
    breakpoint: str
    x: int
    y: int
    w: int
    h: int
    static: Optional[bool]

class MetricsResponse(BaseModel):
    id: str
    is_editable: bool
    records: list[dict]
    layouts: list[LayoutItemResponse]