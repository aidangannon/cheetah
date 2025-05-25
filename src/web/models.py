from datetime import datetime
from typing import Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, validator, Field, ConfigDict


class SystemStatusSchema(BaseModel):
    application: bool
    database: bool


class LayoutConfigSchema(BaseModel):
    breakpoint: str
    x: int
    y: int
    w: int
    h: int
    static: Optional[bool]

class AnalyticsResponseSchema(BaseModel):
    id: str
    is_mutable: bool
    records: list[dict[str, Any]]
    layouts: list[LayoutConfigSchema]

class ConfigurationCreateSchema(BaseModel):
    is_mutable: bool
    layouts: list[LayoutConfigSchema]
    statement_generation_prompt: str

class DataEntryCreateSchema(BaseModel):
    decay_value: float = None
    decay_rate: float = None
    items_flagged: int = None
    notification_type: str = None
    notification_category: str = None

class ResourceCreatedSchema(BaseModel):
    id: str