import logging

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