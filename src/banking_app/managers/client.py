from sqlalchemy import Select
from sqlalchemy import Insert
from sqlalchemy.orm import joinedload

from typing import Any
from typing import Type

from src.banking_app.managers.base import BaseManager
from src.banking_app.models.client import Client


class ClientManager(BaseManager):
    @property
    def model(self) -> Type[Client]:
        return Client

    def filter(self, **kwargs) -> Select:
        statement = (
            super().filter(**kwargs)
            .options(joinedload(self.model.client_status))
        )
        return statement

    def create(self, **kwargs) -> Insert:
        kwargs.setdefault('status', 200)
        statement = (
            super().create(**kwargs)
            .options(joinedload(self.model.client_status))
        )
        return statement

    def bulk_create(self, list_kwargs: list[dict[str, Any]]) -> Insert:
        [kwargs.setdefault('status', 200) for kwargs in list_kwargs]
        statement = (
            super().bulk_create(list_kwargs)
            .options(joinedload(self.model.client_status))
        )
        return statement
