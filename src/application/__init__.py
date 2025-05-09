from src.crosscutting import auto_slots


@auto_slots
class HealthCheckService:

    def __init__(self):
        ...

    def __call__(self):
        ...