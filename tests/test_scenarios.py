import uuid
from http import HTTPStatus

from tests.steps import HealthCheckScenario, GetMetricsScenario


def test_get_health():
    scenario = HealthCheckScenario()
    scenario \
        .given_i_have_an_app_running() \
        .when_the_get_health_endpoint_is_called() \
        .then_the_status_code_should_be_ok() \
        .then_the_response_should_be_healthy() \
        .then_an_info_log_indicates_the_endpoint_was_called()

    scenario \
        .runner \
        .assert_all()


def test_get_metrics_when_invalid_id_is_used():
    scenario = GetMetricsScenario()
    scenario \
        .given_i_have_an_app_running() \
        .when_the_get_health_endpoint_is_called_with_metric_configuration_id("notauuid4") \
        .then_the_status_code_should_be(400) \
        .then_an_error_log_indicates_a_validation_error()

    scenario \
        .runner \
        .assert_all()


def test_get_metrics_when_metric_not_found():
    scenario = GetMetricsScenario()
    scenario \
        .given_i_have_an_app_running() \
        .when_the_get_health_endpoint_is_called_with_metric_configuration_id(str(uuid.uuid4())) \
        .then_the_status_code_should_be(404) \
        .then_an_info_log_indicates_endpoint_called()

    scenario \
        .runner \
        .assert_all()


def ignore_test_get_metrics_when_metric_exists():
    scenario = GetMetricsScenario()
    scenario \
        .given_i_have_an_app_running() \
        .when_the_get_health_endpoint_is_called_with_metric_configuration_id("def1fdce-dac9-4c5a-a4a1-d7cbd01f6ed6") \
        .then_the_status_code_should_be(200) \
        .then_the_response_body_should_match_expected_metric() \
        .then_an_info_log_indicates_endpoint_called()

    scenario \
        .runner \
        .assert_all()