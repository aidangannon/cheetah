from tests.steps import HealthCheckScenario


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