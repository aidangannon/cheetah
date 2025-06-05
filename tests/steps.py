import datetime
import logging
import uuid

from autofixture import AutoFixture

from src.web.models import AnalyticsResponseSchema, LayoutConfigSchema, ConfigurationCreateSchema, DataEntryCreateSchema
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
            operation="get_system_health")
        return self


class GetDatasetScenario:

    def __init__(self, ctx: ScenarioContext) -> None:
        self.day_range = 30
        self.start_date = datetime.date(2025, 6, 1)
        self.end_date = datetime.date(2025, 6, 30)
        self.ctx = ctx
        self.runner = ctx.runner

    @step
    def given_i_have_an_app_running(self):
        return self

    @step
    def when_the_get_metrics_endpoint_is_called_with_dataset_config_id(self, dataset_id: str):
        self.dataset_id = dataset_id
        self.test_token = str(uuid.uuid4())
        self.response = self.ctx.client.get(f"/data/{self.dataset_id}", headers=DEFAULT_REQUEST_HEADERS)
        return self

    @step
    def when_the_get_metrics_endpoint_is_called_with_dataset_config_id_and_params(
            self,
            dataset_id: str,
            **kwargs
    ):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.dataset_id = dataset_id
        self.response = self.ctx.client.get(f"/data/{self.dataset_id}", params=kwargs, headers=DEFAULT_REQUEST_HEADERS)
        return self

    @step
    def then_the_status_code_should_be(self, status_code: int):
        self.ctx.test_case.assertEqual(self.response.status_code,  status_code)
        return self

    @step
    def then_the_response_body_should_match_expected_metric(self):
        expected_response = AnalyticsResponseSchema(
            id="def1fdce-dac9-4c5a-a4a1-d7cbd01f6ed6",
            is_mutable=True,
            records=[
                {
                    'day': '2025-08-01',
                    'cost_avoided': 120.5
                }
            ],
            layouts=[
                LayoutConfigSchema(
                    breakpoint="lg",
                    coordinates=[0, 20, 5, 4],  # [x, y, w, h]
                    static=False
                ),
                LayoutConfigSchema(
                    breakpoint='md',
                    coordinates=[0, 10, 1, 4],  # [x, y, w, h]
                    static=None
                )
            ])
        actual_response = AnalyticsResponseSchema.model_validate(self.response.json())

        self.ctx.test_case.assertEqual(expected_response, actual_response)
        return self

    @step
    def then_the_response_body_should_match_expected_date_range_filtered_metric(self):
        expected_response = AnalyticsResponseSchema(
            id="c797b618-df12-45f7-bbb2-cc6695a48e46",
            is_mutable=True,
            records=[
                {
                    "notification_type": "Critical",
                    "total_alerts": 1
                },
                {
                    "notification_type": "Warning",
                    "total_alerts": 1
                }
            ],
            layouts=[
                LayoutConfigSchema(
                    breakpoint="lg",
                    coordinates=[0, 24, 5, 10],  # [x, y, w, h]
                    static=False
                ),
                LayoutConfigSchema(
                    breakpoint='md',
                    coordinates=[0, 24, 1, 10],  # [x, y, w, h]
                    static=None
                )
            ])
        actual_response = AnalyticsResponseSchema.model_validate(self.response.json())

        self.ctx.test_case.assertEqual(expected_response, actual_response)
        return self

    @step
    def then_the_response_body_should_match_expected_day_range_filtered_metric(self):
        expected_response = AnalyticsResponseSchema(
            id="def1fdce-dac9-4c5a-a4a1-d7cbd01f6ed6",
            is_mutable=True,
            records=[],
            layouts=[
                LayoutConfigSchema(
                    breakpoint="lg",
                    coordinates=[0, 20, 5, 4],  # [x, y, w, h]
                    static=False
                ),
                LayoutConfigSchema(
                    breakpoint='md',
                    coordinates=[0, 10, 1, 4],  # [x, y, w, h]
                    static=None
                )
            ])
        actual_response = AnalyticsResponseSchema.model_validate(self.response.json())

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
            operation="get_analytics_dataset",
            id=self.dataset_id,
            start_date=self.start_date,
            end_date=self.end_date,
            day_range=self.day_range)
        return self


class CreateDatasetConfigScenario:

    def __init__(self, ctx: ScenarioContext):
        self.ctx = ctx
        self.runner = ctx.runner
        self.dataset_config = ConfigurationCreateSchema(
            is_mutable=True,
            layouts=[
                LayoutConfigSchema(
                    static=True,
                    coordinates=[1, 1, 1, 1],  # [x, y, w, h]
                    breakpoint="md"
                ),
                LayoutConfigSchema(
                    static=False,
                    coordinates=[2, 4, 5, 1],  # [x, y, w, h]
                    breakpoint="lg"
                )
            ],
            statement_generation_prompt="shut up and dance"
        )
        self.data_point = DataEntryCreateSchema(
            decay_value=15.3,
            decay_rate=8.1,
            items_flagged=2,
            notification_type="Critical",
            notification_category="Alert"
        )

    @step
    def given_i_have_an_app_running(self):
        return self

    @step
    def when_the_create_dataset_config_endpoint_is_called_with_dataset_config(self):
        self.create_response = self.ctx.client.post(
            f"/data",
            json=self.dataset_config.model_dump(),
            headers=DEFAULT_REQUEST_HEADERS
        )
        self.ctx.test_case.assertEqual(self.create_response.status_code, 201)
        self.dataset_config_id = self.create_response.json()["id"]
        return self

    @step
    def and_data_is_created_for_the_dataset(self):
        create_data_response = self.ctx.client.post(
            f"/data/{self.dataset_config_id}/data-points",
            json=self.data_point.model_dump(),
            headers=DEFAULT_REQUEST_HEADERS
        )
        self.ctx.test_case.assertEqual(create_data_response.status_code, 201)
        return self

    @step
    def then_an_info_log_indicates_endpoint_called(self):
        self.ctx.test_case.assert_there_is_log_with(self.ctx.logger,
            log_level=logging.INFO,
            message="Endpoint called",
            operation="create_data_point",
            dataset_id=self.dataset_config_id,
            decay_rate=self.data_point.decay_rate,
            decay_value=self.data_point.decay_value,
            notification_type=self.data_point.notification_type,
            notification_category=self.data_point.notification_category)
        return self

    @step
    def then_the_status_code_should_be(self, status_code: int):
        self.ctx.test_case.assertEqual(self.create_response.status_code, status_code)
        return self

    @step
    def then_the_dataset_should_have_been_created(self):
        expected_data_response = AnalyticsResponseSchema(
            id=self.dataset_config_id,
            is_mutable=True,
            layouts=[
                LayoutConfigSchema(
                    static=True,
                    coordinates=[1, 1, 1, 1],  # [x, y, w, h]
                    breakpoint="md"
                ),
                LayoutConfigSchema(
                    static=False,
                    coordinates=[2, 4, 5, 1],  # [x, y, w, h]
                    breakpoint="lg"
                )
            ],
            records=[self.data_point.model_dump()]
        )
        dataset_config_id = self.create_response.json()["id"]
        read_response = self.ctx.client.get(f"/data/{dataset_config_id}", headers=DEFAULT_REQUEST_HEADERS)
        actual_data_aggregate = AnalyticsResponseSchema.model_validate(read_response.json())
        self.ctx.test_case.assertEqual(expected_data_response, actual_data_aggregate)
        return self


class CreateDataPointScenario:

    def __init__(self, ctx: ScenarioContext):
        self.ctx = ctx
        self.runner = ctx.runner
        self.data_point = DataEntryCreateSchema(
            decay_value=10.5,
            decay_rate=5.2,
            items_flagged=3,
            notification_type="Warning",
            notification_category="System"
        )
        print("")

    @step
    def given_i_have_an_app_running(self):
        return self

    @step
    def when_the_create_data_point_endpoint_is_called(self, config_id: str):
        self.config_id = config_id
        self.response = self.ctx.client.post(
            f"/data/{config_id}/data-points",
            json=self.data_point.model_dump(),
            headers=DEFAULT_REQUEST_HEADERS
        )
        return self

    @step
    def then_an_info_log_indicates_endpoint_called(self):
        self.ctx.test_case.assert_there_is_log_with(self.ctx.logger,
            log_level=logging.INFO,
            message="Endpoint called",
            operation="create_data_point",
            dataset_id=self.config_id,
            decay_rate=self.data_point.decay_rate,
            decay_value=self.data_point.decay_value,
            notification_type=self.data_point.notification_type,
            notification_category=self.data_point.notification_category)
        return self

    @step
    def then_the_status_code_should_be(self, status_code: int):
        self.ctx.test_case.assertEqual(self.response.status_code, status_code)
        return self