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
        .then_an_info_log_indicates_the_endpoint_was_called()

    scenario \
        .runner \
        .assert_all()