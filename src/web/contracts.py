from datetime import datetime
from typing import Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, validator, Field, ConfigDict


class HealthCheckResponse(BaseModel):
    application: bool
    database: bool


class LayoutItemContract(BaseModel):
    breakpoint: str
    x: int
    y: int
    w: int
    h: int
    static: Optional[bool]

class MetricsResponse(BaseModel):
    id: str
    is_editable: bool
    records: list[dict[str, Any]]
    layouts: list[LayoutItemContract]

class CreateMetricConfigurationRequest(BaseModel):
    is_editable: bool
    layouts: list[LayoutItemContract]
    query_generation_prompt: str

class CreateMetricRequest(BaseModel):
    obsolescence_val: float = None
    obsolescence: float = None
    parts_flagged: int = None
    alert_type: str = None
    alert_category: str = None

class CreatedResponse(BaseModel):
    id: str