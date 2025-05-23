from src.core import MetricConfigurationAggregate, LayoutItem
from src.web.contracts import MetricsResponse, LayoutItemContract, CreateMetricConfiguration
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

def map_metric_configuration_contract_to_domain(create_request: CreateMetricConfiguration) -> MetricConfigurationAggregate:
    config_id = str(uuid.uuid4())
    query_id = str(uuid.uuid4())
    return MetricConfigurationAggregate(
        id=config_id,
        query_id=query_id,
        is_editable=create_request.is_editable,
        layouts=[map_contract_layout_to_domain(x, item=config_id) for x in create_request.layouts]
    )