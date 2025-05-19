import datetime
import logging

from src.web.contracts import MetricsResponse, LayoutItemResponse
from tests import step, assert_there_is_log_with, FastApiScenarioRunner


class HealthCheckScenario:

    def __init__(self):
        self.runner = FastApiScenarioRunner()

    @step
    def given_i_have_an_app_running(self):
        return self

    @step
    def when_the_get_health_endpoint_is_called(self):
        self.response = self.runner.client.get("/health")
        return self

    @step
    def then_the_status_code_should_be_ok(self):
        assert self.response.status_code == 200
        return self

    @step
    def then_the_response_should_be_healthy(self):
        response_body = self.response.json()
        assert response_body == {"application": True, "database": True}, f"actual - {response_body}"
        return self

    @step
    def then_an_info_log_indicates_the_endpoint_was_called(self):
        assert_there_is_log_with(self.runner.test_logger,
            log_level=logging.INFO,
            message="Endpoint called",
            scoped_vars={"operation": "get_health"})
        return self


class GetMetricsScenario:

    def __init__(self):
        self.runner = FastApiScenarioRunner()

    @step
    def given_i_have_an_app_running(self):
        return self

    @step
    def when_the_get_health_endpoint_is_called_with_metric_configuration_id(self, metric_id: str):
        self.metric_id = metric_id
        self.response = self.runner.client.get(f"/metrics/{self.metric_id}")
        return self

    @step
    def then_the_status_code_should_be(self, status_code: int):
        assert self.response.status_code == status_code, f"Actual status code is {self.response.status_code}"
        return self

    @step
    def then_the_response_body_should_match_expected_metric(self):
        expected_response = MetricsResponse(
            id="def1fdce-dac9-4c5a-a4a1-d7cbd01f6ed6",
            is_editable=True,
            records=[
                {
                    'day': '2025-07-15',
                    'cost_avoided': 80.25
                },
                {
                    'day': '2025-08-01',
                    'cost_avoided': 120.5
                }
            ],
            layouts=[
                LayoutItemResponse(
                    id="*",
                    item_id="def1fdce-dac9-4c5a-a4a1-d7cbd01f6ed6",
                    breakpoint="lg",
                    h=4,
                    w=5,
                    x=0,
                    y=20,
                    static=False
                ),
                LayoutItemResponse(
                    id="*",
                    item_id="def1fdce-dac9-4c5a-a4a1-d7cbd01f6ed6",
                    breakpoint='md',
                    h=4,
                    w=1,
                    x=0,
                    y=10
                )
            ])
        actual_response = MetricsResponse.parse_obj(self.response.json())

        exclusions = {"layouts": {"__all__": {"id"}}}

        assert expected_response.dict(exclude=exclusions) == actual_response.dict(exclude=exclusions),\
            f"expected - {expected_response.dict()} actual - {actual_response.dict()}"
        return self

    @step
    def then_an_error_log_indicates_a_validation_error(self):
        assert_there_is_log_with(self.runner.test_logger,
            log_level=logging.ERROR,
            message="Error occurred")
        return self

    @step
    def then_an_info_log_indicates_endpoint_called(self):
        assert_there_is_log_with(self.runner.test_logger,
            log_level=logging.INFO,
            message="Endpoint called",
            scoped_vars={"operation": "get_metrics", "id": self.metric_id})
        return self