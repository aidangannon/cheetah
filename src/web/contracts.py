from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic.v1 import BaseModel, validator


class MetricRecordResponse(BaseModel):
    metric_id: str
    date: datetime
    obsolescence_val: Optional[float]
    parts_flagged: Optional[int]
    alert_type: Optional[str]
    alert_category: Optional[str]

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
    metrics: list[MetricRecordResponse]
    layouts: list[LayoutItemResponse]