from datetime import timezone, datetime

from src.core import DatasetConfigAggregate, ViewConfig, DataPoint
from src.web.contracts import DataResponse, ViewConfigContract, CreateDatasetConfigRequest, CreateDataPointRequest
import uuid


def map_dataset_aggregate_to_contract(dataset_agg: DatasetConfigAggregate) -> DataResponse:
    return DataResponse(
        id=dataset_agg.id,
        is_mutable=dataset_agg.is_mutable,
        records=dataset_agg.records,
        layouts=[map_view_to_contract(x) for x in dataset_agg.layouts]
    )


def map_view_to_contract(view: ViewConfig) -> ViewConfigContract:
    return ViewConfigContract(
        breakpoint=view.breakpoint,
        x=view.x,
        y=view.y,
        w=view.w,
        h=view.h,
        static=view.static
    )

def map_contract_view_to_domain(view: ViewConfigContract, item: str) -> ViewConfig:
    return ViewConfig(
        id=str(uuid.uuid4()),
        element_id=item,
        breakpoint=view.breakpoint,
        x=view.x,
        y=view.y,
        w=view.w,
        h=view.h,
        static=view.static
    )

def map_dataset_config_contract_to_domain(create_request: CreateDatasetConfigRequest) -> DatasetConfigAggregate:
    config_id = str(uuid.uuid4())
    statement_id = str(uuid.uuid4())
    return DatasetConfigAggregate(
        id=config_id,
        statement_id=statement_id,
        is_mutable=create_request.is_mutable,
        layouts=[map_contract_view_to_domain(x, item=config_id) for x in create_request.layouts]
    )

def map_datapoint_contract_to_domain(create_request: CreateDataPointRequest) -> DataPoint:
    record_id = str(uuid.uuid4())
    return DataPoint(
        dataset_id=record_id,
        timestamp=datetime.now(),
        decay_value=create_request.decay_value,
        decay_rate=create_request.decay_rate,
        items_flagged=create_request.items_flagged,
        notification_type=create_request.notification_type,
        notification_category=create_request.notification_category
    )