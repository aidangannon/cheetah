import uuid
from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock
from uuid import UUID

from src.application.mappers import map_metric_aggregate_to_contract, map_layout_to_contract, \
    map_contract_layout_to_domain, map_metric_record_contract_to_domain, map_metric_configuration_contract_to_domain
from src.core import LayoutItem, MetricConfigurationAggregate
from autofixture import AutoFixture

from src.web.contracts import LayoutItemContract, CreateMetricRequest, CreateMetricConfigurationRequest

DEFAULT_UUID = "12345678-1234-5678-1234-567812345678"
DEFAULT_DATETIME = datetime(2025, 8, 8, 12, 0, 0)


class TestMetricsMappers(TestCase):

    def setUp(self):
        self.fixture = AutoFixture()

    def test_map_to_response(self):
        # arrange
        metric_aggregate = self.fixture.create(MetricConfigurationAggregate)

        # act
        response = map_metric_aggregate_to_contract(metric_aggregate)

        # assert
        self.assertEqual(response.id, metric_aggregate.id)
        self.assertEqual(response.records, metric_aggregate.records)
        self.assertEqual(response.is_editable, metric_aggregate.is_editable)
        self.assertEqual([layout.breakpoint for layout in response.layouts], [layout.breakpoint for layout in metric_aggregate.layouts])

    @patch("uuid.uuid4", return_value=UUID(DEFAULT_UUID))
    def test_map_metric_configuration_contract_to_domain(self, _):
        # arrange
        layouts = [
            LayoutItemContract(
                breakpoint="sm",
                x=1,
                y=2,
                w=3,
                h=4,
                static=True
            ),
            LayoutItemContract(
                breakpoint="lg",
                x=5,
                y=6,
                w=7,
                h=8,
                static=False
            )
        ]
        create_request = CreateMetricConfigurationRequest(
            is_editable=True,
            layouts=layouts,
            query_generation_prompt="anything"
        )

        # act
        result = map_metric_configuration_contract_to_domain(create_request)

        # assert
        self.assertEqual(result.id, DEFAULT_UUID)
        self.assertEqual(result.query_id, DEFAULT_UUID)
        self.assertTrue(result.is_editable)
        self.assertEqual(len(result.layouts), len(create_request.layouts))

        # Assuming map_contract_layout_to_domain is tested separately and patched
        for layout_result, layout_contract in zip(result.layouts, create_request.layouts):
            self.assertEqual(layout_result.item_id, DEFAULT_UUID)  # from parent config_id
            self.assertEqual(layout_result.breakpoint, layout_contract.breakpoint)
            self.assertEqual(layout_result.x, layout_contract.x)
            self.assertEqual(layout_result.y, layout_contract.y)
            self.assertEqual(layout_result.w, layout_contract.w)
            self.assertEqual(layout_result.h, layout_contract.h)
            self.assertEqual(layout_result.static, layout_contract.static)


class TestLayoutsMappers(TestCase):

    def setUp(self):
        self.fixture = AutoFixture()

    def test_map_to_response(self):
        # arrange
        layout = self.fixture.create(LayoutItem)

        # act
        response = map_layout_to_contract(layout)

        # assert
        self.assertEqual(response.breakpoint, layout.breakpoint)
        self.assertEqual(response.w, layout.w)
        self.assertEqual(response.x, layout.x)
        self.assertEqual(response.h, layout.h)
        self.assertEqual(response.static, layout.static)
        self.assertEqual(response.y, layout.y)

    @patch("uuid.uuid4", return_value=UUID(DEFAULT_UUID))
    def test_map_contract_layout_to_domain(self, _):
        # arrange
        layout_contract = LayoutItemContract(
            breakpoint="md",
            x=1,
            y=2,
            w=3,
            h=4,
            static=True
        )
        item_id = str(uuid.uuid4())

        # act
        result = map_contract_layout_to_domain(layout_contract, item_id)

        # assert
        self.assertEqual(result.id, DEFAULT_UUID)
        self.assertEqual(result.item_id, item_id)
        self.assertEqual(result.breakpoint, layout_contract.breakpoint)
        self.assertEqual(result.x, layout_contract.x)
        self.assertEqual(result.y, layout_contract.y)
        self.assertEqual(result.w, layout_contract.w)
        self.assertEqual(result.h, layout_contract.h)
        self.assertEqual(result.static, layout_contract.static)


class TestMetricRecordsMappers(TestCase):

    def setUp(self):
        self.fixture = AutoFixture()

    @patch("uuid.uuid4", return_value=UUID(DEFAULT_UUID))
    def test_map_metric_record_contract_to_domain(self, _):
        # arrange
        create_request = self.fixture.create(CreateMetricRequest)

        # act
        result = map_metric_record_contract_to_domain(create_request)

        # assert
        self.assertEqual(result.metric_id, DEFAULT_UUID)
        self.assertTrue(datetime.now() - timedelta(minutes=5) <= result.date <= datetime.now())
        self.assertEqual(result.obsolescence_val, create_request.obsolescence_val)
        self.assertEqual(result.obsolescence, create_request.obsolescence)
        self.assertEqual(result.parts_flagged, create_request.parts_flagged)
        self.assertEqual(result.alert_type, create_request.alert_type)
        self.assertEqual(result.alert_category, create_request.alert_category)