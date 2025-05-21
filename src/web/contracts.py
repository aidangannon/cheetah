from datetime import datetime
from typing import Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, validator, Field, ConfigDict


class LayoutItemResponse(BaseModel):
    breakpoint: str
    x: int
    y: int
    w: int
    h: int
    static: Optional[bool]

class MetricsResponse(BaseModel):
    id: str
    is_editable: bool
    records: list[dict[str, object]]
    layouts: list[LayoutItemResponse]