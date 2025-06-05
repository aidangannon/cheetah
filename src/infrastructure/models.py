from typing import Optional, Any

from sqlalchemy import (
    Table, MetaData, Column, String, Float, DateTime, Integer, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import registry, relationship, foreign

from src.core import DataPoint, DatasetConfig, ViewConfig, SqlStatement, DatasetConfigAggregate

_mappers_started = False

mapper_registry = registry()
metadata = MetaData()

data_points = Table(
    "data_points",
    metadata,
    Column("dataset_id", String, primary_key=True),
    Column("id", String, nullable=True),
    Column("timestamp", DateTime, nullable=True),
    Column("decay_value", Float, nullable=True),
    Column("decay_rate", Float, nullable=True),
    Column("items_flagged", Integer, nullable=True),
    Column("notification_type", String, nullable=True),
    Column("notification_category", String, nullable=True),
)

sql_statements = Table(
    "sql_statements",
    metadata,
    Column("id", String, primary_key=True),
    Column("statement", String, nullable=True),
)

dataset_configs = Table(
    "dataset_configs",
    metadata,
    Column("id", String, primary_key=True),
    Column("statement_id", String, nullable=True),
    Column("is_mutable", Boolean, nullable=True),
)

view_configs = Table(
    "view_configs",
    metadata,
    Column("id", String, primary_key=True),
    Column("element_id", String, nullable=True),
    Column("breakpoint", String, nullable=True),
    Column("coordinates", JSON, nullable=True),  # [x, y, w, h]
    Column("static", Boolean, nullable=True)
)

def start_mappers():
    global _mappers_started
    if _mappers_started:
        return
    _mappers_started = True

    mapper_registry.map_imperatively(DataPoint, data_points)

    mapper_registry.map_imperatively(SqlStatement, sql_statements)

    mapper_registry.map_imperatively(ViewConfig, view_configs)

    mapper_registry.map_imperatively(DatasetConfig, dataset_configs)

    mapper_registry.map_imperatively(
        DatasetConfigAggregate,
        dataset_configs,
        properties={
            "statement": relationship(
                SqlStatement,
                primaryjoin=foreign(dataset_configs.c.statement_id) == sql_statements.c.id,
                backref="dataset_configurations",
                lazy="joined"
            ),
            "layouts": relationship(
                ViewConfig,
                primaryjoin=foreign(view_configs.c.element_id) == dataset_configs.c.id,
                backref="dataset_configuration",
                lazy="joined"
            )
        }
    )