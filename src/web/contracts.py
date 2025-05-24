from datetime import datetime
from typing import Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, validator, Field, ConfigDict


class HealthCheckResponse(BaseModel):
    application: bool
    database: bool


class ViewConfigContract(BaseModel):
    breakpoint: str
    x: int
    y: int
    w: int
    h: int
    static: Optional[bool]

class DataResponse(BaseModel):
    id: str
    is_mutable: bool
    records: list[dict[str, Any]]
    layouts: list[ViewConfigContract]

class CreateDatasetConfigRequest(BaseModel):
    is_mutable: bool
    layouts: list[ViewConfigContract]
    statement_generation_prompt: str

class CreateDataPointRequest(BaseModel):
    decay_value: float = None
    decay_rate: float = None
    items_flagged: int = None
    notification_type: str = None
    notification_category: str = None

class CreatedResponse(BaseModel):
    id: str