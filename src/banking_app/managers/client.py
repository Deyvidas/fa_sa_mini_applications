from sqlalchemy import Delete
from sqlalchemy import Select
from sqlalchemy import Insert
from sqlalchemy.orm import joinedload

from typing import Any
from typing import Type
from typing import TypeAlias
from typing import Union

from src.banking_app.managers.base import BaseManager
from src.banking_app.models.client import Client


Statement: TypeAlias = Union[Delete, Select, Insert]


class ClientManager(BaseManager):
    @property
    def model(self) -> Type[Client]:
        return Client

    def filter(self, **kwargs) -> Select:
        statement = self._enrich_statement(super().filter(**kwargs))
        return statement

    def create(self, **kwargs) -> Insert:
        kwargs.setdefault('status', 200)
        statement = self._enrich_statement(super().create(**kwargs))
        return statement

    def bulk_create(self, list_kwargs: list[dict[str, Any]]) -> Insert:
        [kwargs.setdefault('status', 200) for kwargs in list_kwargs]
        statement = self._enrich_statement(super().bulk_create(list_kwargs))
        return statement

    def delete(self, **kwargs: dict[str, Any]) -> Delete:
        statement = self._enrich_statement(super().delete(**kwargs))
        return statement

    def _enrich_statement(self, statement: Statement):
        statement = (
            statement.
            options(joinedload(self.model.client_status))
        )
        if type(statement) is Select:
            statement = self._enrich_select_statement(statement)
        return statement

    def _enrich_select_statement(self, statement: Select):
        statement = (
            statement.
            order_by(self.model.reg_date.desc()).
            order_by(self.model.full_name.asc())
        )
        return statement
