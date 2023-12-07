from typing import Any
from typing import Type

from sqlalchemy import Insert
from sqlalchemy import Select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload

from src.banking_app.managers.base import SelCreStmt
from src.banking_app.managers.base import SelectCreateManager
from src.banking_app.models.balance import Balance
from src.banking_app.models.client import Client


class BalanceManager(SelectCreateManager):

    @property
    def model(self) -> Type[Balance]:
        return Balance

    def filter(self, **kwargs) -> Select:
        statement = self._enrich_statement(super().filter(**kwargs))
        return statement

    def create(self, **kwargs) -> Insert:
        statement = self._enrich_statement(super().create(**kwargs))
        return statement

    def bulk_create(self, list_kwargs: list[dict[str, Any]]) -> Insert:
        statement = self._enrich_statement(super().bulk_create(list_kwargs))
        return statement

    def _enrich_statement(self, statement: SelCreStmt) -> SelCreStmt:
        """Enrich passed statement and return enriched statement."""

        load_strategy = (
            joinedload(self.model.client).
            joinedload(Client.client_status)
        )
        if isinstance(statement, Insert):
            load_strategy = (
                selectinload(self.model.client).
                joinedload(Client.client_status)
            )

        statement = statement.options(load_strategy)
        return statement
