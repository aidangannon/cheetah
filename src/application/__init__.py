from src.core import UnitOfWork
from src.crosscutting import auto_slots


@auto_slots
class HealthCheckService:

    def __init__(self, unit_of_work: UnitOfWork):
        ...

    def __call__(self):
        ...