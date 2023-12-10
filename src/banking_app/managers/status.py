from typing import Type

from src.banking_app.models.status import Status
from src.banking_app.managers.base import BaseManager


class StatusManager(BaseManager):

    @property
    def model(self) -> Type[Status]:
        return Status
