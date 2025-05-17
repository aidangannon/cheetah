from typing import Optional, Any

from sqlalchemy import (
    Table, MetaData, Column, String, Float, DateTime, Integer, Boolean, ForeignKey
)
from sqlalchemy.orm import registry, relationship, foreign

from src.core import MetricRecord, MetricConfiguration, LayoutItem, Query, MetricConfigurationAggregate

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

queries = Table(
    "queries",
    metadata,
    Column("id", String, primary_key=True),
    Column("query", String, nullable=True),
)

metric_configurations = Table(
    "metric_configurations",
    metadata,
    Column("id", String, primary_key=True),
    Column("query_id", String, nullable=True),
    Column("is_editable", Boolean, nullable=True),
)

layout_items = Table(
    "layout_items",
    metadata,
    Column("id", String, primary_key=True),
    Column("item_id", String, nullable=True),
    Column("breakpoint", String, nullable=True),
    Column("x", Integer, nullable=True),
    Column("y", Integer, nullable=True),
    Column("w", Integer, nullable=True),
    Column("h", Integer, nullable=True),
    Column("static", Boolean, nullable=True)
)

def start_mappers():

    mapper_registry.map_imperatively(MetricRecord, metrics)

    mapper_registry.map_imperatively(Query, queries)

    mapper_registry.map_imperatively(LayoutItem, layout_items)

    mapper_registry.map_imperatively(MetricConfiguration, metric_configurations)

    mapper_registry.map_imperatively(
        MetricConfigurationAggregate,
        metric_configurations,
        properties={
            "query": relationship(
                Query,
                primaryjoin=metric_configurations.c.query_id == foreign(queries.c.id),
                backref="metric_configurations"
            ),
            "layouts": relationship(
                LayoutItem,
                primaryjoin=layout_items.c.item_id == foreign(metric_configurations.c.id),
                backref="metric_configuration"
            )
        }
    )
