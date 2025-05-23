import datetime
import logging
import uuid

from autofixture import AutoFixture

from src.web.contracts import MetricsResponse, LayoutItemContract, CreateMetricConfigurationRequest, CreateMetricRequest
from tests import step, ScenarioContext

DEFAULT_REQUEST_HEADERS = {"Authorization": "Bearer test"}

class HealthCheckScenario:

    def __init__(self, ctx: ScenarioContext) -> None:
        self.ctx = ctx

    @step
    def given_i_have_an_app_running(self):
        return self

    @step
    def when_the_get_health_endpoint_is_called(self):
        self.response = self.ctx.client.get("/health")
        return self

    @step
    def then_the_status_code_should_be_ok(self):
        self.ctx.test_case.assertEqual(self.response.status_code, 200)
        return self

    @step
    def then_the_response_should_be_healthy(self):
        response_body = self.response.json()
        self.ctx.test_case.assertEqual(response_body, {"application": True, "database": True})
        return self

    @step
    def then_an_info_log_indicates_the_endpoint_was_called(self):
        self.ctx.test_case.assert_there_is_log_with(self.ctx.logger,
            log_level=logging.INFO,
            message="Endpoint called",
            operation="get_health")
        return self


class GetMetricsScenario:

    def __init__(self, ctx: ScenarioContext) -> None:
        self.day_range = 30
        self.start_date = datetime.date(2025, 6, 1)
        self.end_date = datetime.date(2025, 6, 30)
        self.ctx = ctx

    @step
    def given_i_have_an_app_running(self):
        return self

    @step
    def when_the_get_metrics_endpoint_is_called_with_metric_configuration_id(self, metric_id: str):
        self.metric_id = metric_id
        self.test_token = str(uuid.uuid4())
        self.response = self.ctx.client.get(f"/metrics/{self.metric_id}", headers=DEFAULT_REQUEST_HEADERS)
        return self

    @step
    def when_the_get_metrics_endpoint_is_called_with_metric_configuration_id_and_params(
            self,
            metric_id: str,
            **kwargs
    ):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.metric_id = metric_id
        self.response = self.ctx.client.get(f"/metrics/{self.metric_id}", params=kwargs, headers=DEFAULT_REQUEST_HEADERS)
        return self

    @step
    def then_the_status_code_should_be(self, status_code: int):
        self.ctx.test_case.assertEqual(self.response.status_code,  status_code)
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
                LayoutItemContract(
                    breakpoint="lg",
                    h=4,
                    w=5,
                    x=0,
                    y=20,
                    static=False
                ),
                LayoutItemContract(
                    breakpoint='md',
                    h=4,
                    w=1,
                    x=0,
                    y=10,
                    static=None
                )
            ])
        actual_response = MetricsResponse.model_validate(self.response.json())

        self.ctx.test_case.assertEqual(expected_response, actual_response)
        return self

    @step
    def then_the_response_body_should_match_expected_date_range_filtered_metric(self):
        expected_response = MetricsResponse(
            id="c797b618-df12-45f7-bbb2-cc6695a48e46",
            is_editable=True,
            records=[
                {
                    "alert_type": "Critical",
                    "total_alerts": 1
                },
                {
                    "alert_type": "Warning",
                    "total_alerts": 1
                }
            ],
            layouts=[
                LayoutItemContract(
                    breakpoint="lg",
                    h=10,
                    w=5,
                    x=0,
                    y=24,
                    static=False
                ),
                LayoutItemContract(
                    breakpoint='md',
                    h=10,
                    w=1,
                    x=0,
                    y=24,
                    static=None
                )
            ])
        actual_response = MetricsResponse.model_validate(self.response.json())

        self.ctx.test_case.assertEqual(expected_response, actual_response)
        return self

    @step
    def then_the_response_body_should_match_expected_day_range_filtered_metric(self):
        expected_response = MetricsResponse(
            id="def1fdce-dac9-4c5a-a4a1-d7cbd01f6ed6",
            is_editable=True,
            records=[],
            layouts=[
                LayoutItemContract(
                    breakpoint="lg",
                    h=4,
                    w=5,
                    x=0,
                    y=20,
                    static=False
                ),
                LayoutItemContract(
                    breakpoint='md',
                    h=4,
                    w=1,
                    x=0,
                    y=10,
                    static=None
                )
            ])
        actual_response = MetricsResponse.model_validate(self.response.json())

        self.ctx.test_case.assertEqual(expected_response, actual_response)
        return self

    @step
    def then_an_error_log_indicates_a_validation_error(self):
        self.ctx.test_case.assert_there_is_log_with(self.ctx.logger,
            log_level=logging.WARNING,
            message="Validation error")
        return self

    @step
    def then_an_info_log_indicates_endpoint_called(self):
        self.ctx.test_case.assert_there_is_log_with(self.ctx.logger,
            log_level=logging.INFO,
            message="Endpoint called",
            operation="get_metrics",
            id=self.metric_id,
            start_date=self.start_date,
            end_date=self.end_date,
            day_range=self.day_range)
        return self


class CreateMetricConfigurationScenario:

    def __init__(self, ctx: ScenarioContext):
        self.ctx = ctx
        self.metric_config = CreateMetricConfigurationRequest(
            is_editable=True,
            layouts=[
                LayoutItemContract(
                    static=True,
                    x=1,
                    y=1,
                    h=1,
                    w=1,
                    breakpoint="md"
                ),
                LayoutItemContract(
                    static=False,
                    x=2,
                    y=4,
                    h=1,
                    w=5,
                    breakpoint="lg"
                )
            ],
            query_generation_prompt="shut up and dance"
        )
        self.metric_record = AutoFixture().create(CreateMetricRequest)

    @step
    def given_i_have_an_app_running(self):
        return self

    @step
    def when_the_create_metric_configuration_endpoint_is_called_with_metric_configuration(self):
        self.create_response = self.ctx.client.post(
            f"/metrics",
            json=self.metric_config.model_dump(),
            headers=DEFAULT_REQUEST_HEADERS
        )
        self.ctx.test_case.assertEqual(self.create_response.status_code, 201)
        self.metric_config_id = self.create_response.json()["id"]
        return self

    @step
    def and_data_is_created_for_the_metric(self):
        create_data_response = self.ctx.client.post(
            f"/metrics/{self.metric_config_id}/metric-records",
            json=self.metric_record.model_dump(),
            headers=DEFAULT_REQUEST_HEADERS
        )
        self.ctx.test_case.assertEqual(create_data_response.status_code, 201)
        return self

    @step
    def then_an_info_log_indicates_endpoint_called(self):
        self.ctx.test_case.assert_there_is_log_with(self.ctx.logger,
            log_level=logging.INFO,
            message="Endpoint called",
            operation="create_metric_record",
            metric_id=self.metric_config_id,
            obsolescence=self.metric_record.obsolescence,
            obsolescence_val=self.metric_record.obsolescence_val,
            alert_type=self.metric_record.alert_type,
            alert_category=self.metric_record.alert_category)
        return self

    @step
    def then_the_status_code_should_be(self, status_code: int):
        self.ctx.test_case.assertEqual(self.create_response.status_code, status_code)
        return self

    @step
    def then_the_metrics_should_have_been_created(self):
        expected_metrics_response = MetricsResponse(
            id=self.metric_config_id,
            is_editable=True,
            layouts=[
                LayoutItemContract(
                    static=True,
                    x=1,
                    y=1,
                    h=1,
                    w=1,
                    breakpoint="md"
                ),
                LayoutItemContract(
                    static=False,
                    x=2,
                    y=4,
                    h=1,
                    w=5,
                    breakpoint="lg"
                )
            ],
            records=[self.metric_record.model_dump()]
        )
        metric_config_id = self.create_response.json()["id"]
        read_response = self.ctx.client.get(f"/metrics/{metric_config_id}", headers=DEFAULT_REQUEST_HEADERS)
        actual_metrics_aggregate = MetricsResponse.model_validate(read_response.json())
        self.ctx.test_case.assertEqual(expected_metrics_response, actual_metrics_aggregate)
        return self


class CreateMetricRecordScenario:

    def __init__(self, ctx: ScenarioContext):
        self.ctx = ctx
        self.metric_record = AutoFixture().create(CreateMetricRequest)
        print("")

    @step
    def given_i_have_an_app_running(self):
        return self

    @step
    def when_the_create_metric_data_endpoint_is_called(self, config_id: str):
        self.config_id = config_id
        self.response = self.ctx.client.post(
            f"/metrics/{config_id}/metric-records",
            json=self.metric_record.model_dump(),
            headers=DEFAULT_REQUEST_HEADERS
        )
        return self

    @step
    def then_an_info_log_indicates_endpoint_called(self):
        self.ctx.test_case.assert_there_is_log_with(self.ctx.logger,
            log_level=logging.INFO,
            message="Endpoint called",
            operation="create_metric_record",
            metric_id=self.config_id,
            obsolescence=self.metric_record.obsolescence,
            obsolescence_val=self.metric_record.obsolescence_val,
            alert_type=self.metric_record.alert_type,
            alert_category=self.metric_record.alert_category)
        return self

    @step
    def then_the_status_code_should_be(self, status_code: int):
        self.ctx.test_case.assertEqual(self.response.status_code, status_code)
        return self