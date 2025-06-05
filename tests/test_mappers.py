import uuid
from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock
from uuid import UUID

from src.application.mappers import map_dataset_aggregate_to_contract, map_view_to_contract, \
    map_contract_view_to_domain, map_datapoint_contract_to_domain, map_dataset_config_contract_to_domain
from src.core import ViewConfig, DatasetConfigAggregate
from autofixture import AutoFixture

from src.web.models import LayoutConfigSchema, DataEntryCreateSchema, ConfigurationCreateSchema

DEFAULT_UUID = "12345678-1234-5678-1234-567812345678"
DEFAULT_DATETIME = datetime(2025, 8, 8, 12, 0, 0)


class TestMetricsMappers(TestCase):

    def setUp(self):
        self.fixture = AutoFixture()

    def test_map_to_response(self):
        # arrange
        metric_aggregate = self.fixture.create(DatasetConfigAggregate)

        # act
        response = map_dataset_aggregate_to_contract(metric_aggregate)

        # assert
        self.assertEqual(response.id, metric_aggregate.id)
        self.assertEqual(response.records, metric_aggregate.records)
        self.assertEqual(response.is_mutable, metric_aggregate.is_mutable)
        self.assertEqual([layout.breakpoint for layout in response.layouts], [layout.breakpoint for layout in metric_aggregate.layouts])

    @patch("uuid.uuid4", return_value=UUID(DEFAULT_UUID))
    def test_map_dataset_config_contract_to_domain(self, _):
        # arrange
        layouts = [
            LayoutConfigSchema(
                breakpoint="sm",
                coordinates=[1, 2, 3, 4],  # [x, y, w, h]
                static=True
            ),
            LayoutConfigSchema(
                breakpoint="lg",
                coordinates=[5, 6, 7, 8],  # [x, y, w, h]
                static=False
            )
        ]
        create_request = ConfigurationCreateSchema(
            is_mutable=True,
            layouts=layouts,
            statement_generation_prompt="anything"
        )

        # act
        result = map_dataset_config_contract_to_domain(create_request)

        # assert
        self.assertEqual(result.id, DEFAULT_UUID)
        self.assertEqual(result.statement_id, DEFAULT_UUID)
        self.assertTrue(result.is_mutable)
        self.assertEqual(len(result.layouts), len(create_request.layouts))

        # Assuming map_contract_layout_to_domain is tested separately and patched
        for layout_result, layout_contract in zip(result.layouts, create_request.layouts):
            self.assertEqual(layout_result.element_id, DEFAULT_UUID)  # from parent config_id
            self.assertEqual(layout_result.breakpoint, layout_contract.breakpoint)
            self.assertEqual(layout_result.coordinates, layout_contract.coordinates)
            self.assertEqual(layout_result.static, layout_contract.static)


class TestLayoutsMappers(TestCase):

    def setUp(self):
        self.fixture = AutoFixture()

    def test_map_to_response(self):
        # arrange
        layout = self.fixture.create(ViewConfig)

        # act
        response = map_view_to_contract(layout)

        # assert
        self.assertEqual(response.breakpoint, layout.breakpoint)
        self.assertEqual(response.coordinates, layout.coordinates)
        self.assertEqual(response.static, layout.static)

    @patch("uuid.uuid4", return_value=UUID(DEFAULT_UUID))
    def test_map_contract_view_to_domain(self, _):
        # arrange
        layout_contract = LayoutConfigSchema(
            breakpoint="md",
            coordinates=[1, 2, 3, 4],  # [x, y, w, h]
            static=True
        )
        item_id = str(uuid.uuid4())

        # act
        result = map_contract_view_to_domain(layout_contract, item_id)

        # assert
        self.assertEqual(result.id, DEFAULT_UUID)
        self.assertEqual(result.element_id, item_id)
        self.assertEqual(result.breakpoint, layout_contract.breakpoint)
        self.assertEqual(result.coordinates, layout_contract.coordinates)
        self.assertEqual(result.static, layout_contract.static)


class TestDataPointMappers(TestCase):

    def setUp(self):
        self.fixture = AutoFixture()

    @patch("uuid.uuid4", return_value=UUID(DEFAULT_UUID))
    def test_map_datapoint_contract_to_domain(self, _):
        # arrange
        create_request = self.fixture.create(DataEntryCreateSchema)

        # act
        result = map_datapoint_contract_to_domain(create_request)

        # assert
        self.assertEqual(result.dataset_id, DEFAULT_UUID)
        self.assertTrue(datetime.now() - timedelta(minutes=5) <= result.timestamp <= datetime.now())
        self.assertEqual(result.decay_value, create_request.decay_value)
        self.assertEqual(result.decay_rate, create_request.decay_rate)
        self.assertEqual(result.items_flagged, create_request.items_flagged)
        self.assertEqual(result.notification_type, create_request.notification_type)
        self.assertEqual(result.notification_category, create_request.notification_category)