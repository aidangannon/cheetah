import logging

from tests import step, assert_there_is_log_with, ScenarioRunner


class HealthCheckScenario:

    def __init__(self):
        self.runner = ScenarioRunner()

    @step
    def given_i_have_an_app_running(self):
        return self

    @step
    def when_the_get_health_endpoint_is_called(self):
        self.runner.client.get("/health")
        return self

    @step
    def then_an_info_log_indicates_the_endpoint_was_called(self):
        assert_there_is_log_with(self.runner.test_logger,
            log_level=logging.INFO,
            message="Endpoint called",
            scoped_vars={"operation": "get_health"})
        return self