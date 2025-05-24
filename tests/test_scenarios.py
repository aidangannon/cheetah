import datetime
import uuid

from tests import FastApiTestCase, ScenarioContext, ScenarioRunner
from tests.steps import HealthCheckScenario, GetDatasetScenario, CreateDatasetConfigScenario, \
    CreateDataPointScenario


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


class TestGetDatasetScenarios(FastApiTestCase):

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

    def test_get_dataset_when_invalid_id_is_used(self):
        scenario = GetDatasetScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_get_metrics_endpoint_is_called_with_dataset_config_id("notauuid4") \
            .then_the_status_code_should_be(422) \
            .then_an_error_log_indicates_a_validation_error()


    def test_get_dataset_when_dataset_not_found(self):
        scenario = GetDatasetScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_get_metrics_endpoint_is_called_with_dataset_config_id(str(uuid.uuid4())) \
            .then_the_status_code_should_be(404) \
            .then_an_info_log_indicates_endpoint_called()


    def test_get_dataset_when_dataset_exists(self):
        scenario = GetDatasetScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_get_metrics_endpoint_is_called_with_dataset_config_id("def1fdce-dac9-4c5a-a4a1-d7cbd01f6ed6") \
            .then_the_status_code_should_be(200) \
            .then_the_response_body_should_match_expected_metric() \
            .then_an_info_log_indicates_endpoint_called()

    def test_get_dataset_when_dataset_exists_and_date_range_filtering_is_added(self):
        scenario = GetDatasetScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_get_metrics_endpoint_is_called_with_dataset_config_id_and_params(
                "c797b618-df12-45f7-bbb2-cc6695a48e46",
                start_date=datetime.date(2025, 6, 1),
                end_date=datetime.date(2025, 6, 4)) \
            .then_the_status_code_should_be(200) \
            .then_the_response_body_should_match_expected_date_range_filtered_metric() \
            .then_an_info_log_indicates_endpoint_called()

    def test_get_dataset_when_dataset_exists_and_day_range_filtering_is_added(self):
        scenario = GetDatasetScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_get_metrics_endpoint_is_called_with_dataset_config_id_and_params(
                "def1fdce-dac9-4c5a-a4a1-d7cbd01f6ed6",
                day_range=0) \
            .then_the_status_code_should_be(200) \
            .then_the_response_body_should_match_expected_day_range_filtered_metric() \
            .then_an_info_log_indicates_endpoint_called()


class TestCreateDatasetConfigScenarios(FastApiTestCase):

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

    def test_create_dataset_config(self):
        scenario = CreateDatasetConfigScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_create_dataset_config_endpoint_is_called_with_dataset_config() \
            .and_data_is_created_for_the_dataset() \
            .then_the_status_code_should_be(201) \
            .then_the_dataset_should_have_been_created() \
            .then_an_info_log_indicates_endpoint_called()


class TestCreateDataPointScenarios(FastApiTestCase):

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

    def test_create_data_point_when_no_dataset_config_is_present(self):
        scenario = CreateDataPointScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_create_data_point_endpoint_is_called(str(uuid.uuid4())) \
            .then_the_status_code_should_be(404) \
            .then_an_info_log_indicates_endpoint_called()

    def test_create_data_point(self):
        scenario = CreateDataPointScenario(self.context)
        scenario \
            .given_i_have_an_app_running() \
            .when_the_create_data_point_endpoint_is_called("073ac9db-c16e-4d04-9f25-6fc01d4ac380") \
            .then_the_status_code_should_be(201) \
            .then_an_info_log_indicates_endpoint_called()