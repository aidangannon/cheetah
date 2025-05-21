from unittest import TestCase


from src.application.mappers import map_metric_aggregate_to_contract, map_layout_to_contract
from src.core import LayoutItem, MetricConfigurationAggregate
from autofixture import AutoFixture


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