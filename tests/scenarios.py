from tests.steps import HealthCheckScenario


def test_health_check():
    scenario = HealthCheckScenario()
    scenario \
        .given_i_have_a_flask_app_running() \
        .when_my_health_check_endpoint_is_called() \
        .then_i_have_an_endpoint_called_log("hello") \
        .and_then_some_bs_happens()
    scenario.assert_all()