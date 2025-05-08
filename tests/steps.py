import logging

from tests import BaseScenario, step, assert_there_is_log_with


class HealthCheckScenario(BaseScenario):

    @step
    def given_i_have_a_flask_app_running(self):
        ...
        return self

    @step
    def when_my_health_check_endpoint_is_called(self):
        self.client.get("/")
        return self

    @step
    def then_i_have_an_endpoint_called_log(self, _str: str):
        print(_str)
        assert_there_is_log_with(self.test_logger,
            log_level=logging.INFO,
            message="My stuff",
            scoped_vars={"operation": "My stuff"})
        return self

    @step
    def and_then_some_bs_happens(self):
        raise AssertionError()