import uuid
from http import HTTPStatus

from tests import FastApiTestCase, ScenarioContext, ScenarioRunner
from tests.steps import HealthCheckScenario, GetMetricsScenario


class TestHealthCheckScenarios(FastApiTestCase):

    def setUp(self) -> None:
        self.context = ScenarioContext(
            client=self.client,
            test_case=self,
            logger=self.test_logger,
            runner=ScenarioRunner()
        )

    def tearDown(self) -> None:
        self.context \
            .runner \
            .assert_all()

    def test_get_health(self):
        scenario = HealthCheckScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_get_health_endpoint_is_called() \
            .then_the_status_code_should_be_ok() \
            .then_the_response_should_be_healthy() \
            .then_an_info_log_indicates_the_endpoint_was_called()


class TestMetricsScenarios(FastApiTestCase):

    def setUp(self) -> None:
        self.context = ScenarioContext(
            client=self.client,
            test_case=self,
            logger=self.test_logger,
            runner=ScenarioRunner()
        )

    def tearDown(self) -> None:
        self.context \
            .runner \
            .assert_all()

    def test_get_metrics_when_invalid_id_is_used(self):
        scenario = GetMetricsScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_get_health_endpoint_is_called_with_metric_configuration_id("notauuid4") \
            .then_the_status_code_should_be(400) \
            .then_an_error_log_indicates_a_validation_error()


    def test_get_metrics_when_metric_not_found(self):
        scenario = GetMetricsScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_get_health_endpoint_is_called_with_metric_configuration_id(str(uuid.uuid4())) \
            .then_the_status_code_should_be(404) \
            .then_an_info_log_indicates_endpoint_called()


    def test_get_metrics_when_metric_exists(self):
        scenario = GetMetricsScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_get_health_endpoint_is_called_with_metric_configuration_id("def1fdce-dac9-4c5a-a4a1-d7cbd01f6ed6") \
            .then_the_status_code_should_be(200) \
            .then_the_response_body_should_match_expected_metric() \
            .then_an_info_log_indicates_endpoint_called()