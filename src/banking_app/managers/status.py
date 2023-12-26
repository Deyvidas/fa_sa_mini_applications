from src.banking_app.models.status import Status
from src.banking_app.managers.base import BaseManager


class StatusManager(BaseManager):
    model: type[Status] = Status
