from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic.v1 import BaseModel


@dataclass(unsafe_hash=True)
class MetricRecordResponse(BaseModel):
    metric_id: str
    date: datetime
    obsolescence_val: Optional[float]
    parts_flagged: Optional[int]
    alert_type: Optional[str]
    alert_category: Optional[str]

@dataclass(unsafe_hash=True)
class LayoutItemResponse(BaseModel):
    id: str
    item_id: str
    breakpoint: str
    x: int
    y: int
    w: int
    h: int
    static: Optional[bool]

@dataclass(unsafe_hash=True)
class MetricsResponse(BaseModel):
    id: str
    is_editable: bool
    metrics: list[MetricRecordResponse]
    layouts: list[LayoutItemResponse]