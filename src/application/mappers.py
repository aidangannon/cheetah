from datetime import timezone, datetime

from src.core import MetricConfigurationAggregate, LayoutItem, MetricRecord
from src.web.contracts import MetricsResponse, LayoutItemContract, CreateMetricConfigurationRequest, CreateMetricRequest
import uuid


def map_metric_aggregate_to_contract(metric_agg: MetricConfigurationAggregate) -> MetricsResponse:
    return MetricsResponse(
        id=metric_agg.id,
        is_editable=metric_agg.is_editable,
        records=metric_agg.records,
        layouts=[map_layout_to_contract(x) for x in metric_agg.layouts]
    )


def map_layout_to_contract(layout: LayoutItem) -> LayoutItemContract:
    return LayoutItemContract(
        breakpoint=layout.breakpoint,
        x=layout.x,
        y=layout.y,
        w=layout.w,
        h=layout.h,
        static=layout.static
    )

def map_contract_layout_to_domain(layout: LayoutItemContract, item: str) -> LayoutItem:
    return LayoutItem(
        id=str(uuid.uuid4()),
        item_id=item,
        breakpoint=layout.breakpoint,
        x=layout.x,
        y=layout.y,
        w=layout.w,
        h=layout.h,
        static=layout.static
    )

def map_metric_configuration_contract_to_domain(create_request: CreateMetricConfigurationRequest) -> MetricConfigurationAggregate:
    config_id = str(uuid.uuid4())
    query_id = str(uuid.uuid4())
    return MetricConfigurationAggregate(
        id=config_id,
        query_id=query_id,
        is_editable=create_request.is_editable,
        layouts=[map_contract_layout_to_domain(x, item=config_id) for x in create_request.layouts]
    )

def map_metric_record_contract_to_domain(create_request: CreateMetricRequest) -> MetricRecord:
    record_id = str(uuid.uuid4())
    return MetricRecord(
        metric_id=record_id,
        date=datetime.now(),
        obsolescence_val=create_request.obsolescence_val,
        obsolescence=create_request.obsolescence,
        parts_flagged=create_request.parts_flagged,
        alert_type=create_request.alert_type,
        alert_category=create_request.alert_category
    )