from unittest import TestCase

from src.main import app


class FeatureTestCase(TestCase):

    client: Client

    def setUp(self) -> None:
        app.testing = True
        with app.test_client() as client:
            yield client