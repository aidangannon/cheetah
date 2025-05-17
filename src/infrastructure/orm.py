from sqlalchemy import (
    Table, MetaData, Column, String, Float, DateTime, Integer
)
from sqlalchemy.orm import registry

from src.core import MetricRecord

mapper_registry = registry()
metadata = MetaData()

metrics = Table(
    "metrics",
    metadata,
    Column("metric_id", String, primary_key=True),
    Column("id", String, nullable=True),
    Column("date", DateTime, nullable=True),
    Column("obsolescence_val", Float, nullable=True),
    Column("parts_flagged", Integer, nullable=True),
    Column("alert_type", String, nullable=True),
    Column("alert_category", String, nullable=True),
)

def start_mappers():
    mapper_registry.map_imperatively(MetricRecord, metrics)
