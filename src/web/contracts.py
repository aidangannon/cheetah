from datetime import datetime
from typing import Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, validator, Field, ConfigDict


class HealthCheckResponse(BaseModel):
    application: bool
    database: bool


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
    records: list[dict[str, Any]]
    layouts: list[LayoutItemResponse]

class CreateMetricConfiguration(BaseModel):
    is_editable: bool
    layouts: list[LayoutItemResponse]
    query_generation_prompt: str

class CreatedResponse(BaseModel):
    id: str