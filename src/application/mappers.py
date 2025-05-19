from src.core import MetricConfigurationAggregate, LayoutItem
from src.web.contracts import MetricsResponse, LayoutItemResponse


def map_metric_aggregate_to_contract(metric_agg: MetricConfigurationAggregate) -> MetricsResponse:
    return MetricsResponse(
        id=metric_agg.id,
        is_editable=metric_agg.is_editable,
        records=metric_agg.records,
        layouts=[map_layout_to_contract(x) for x in metric_agg.layouts]
    )


def map_layout_to_contract(layout: LayoutItem) -> LayoutItemResponse:
    return LayoutItemResponse(
        breakpoint=layout.breakpoint,
        x=layout.x,
        y=layout.y,
        w=layout.w,
        h=layout.h,
        static=layout.static
    )