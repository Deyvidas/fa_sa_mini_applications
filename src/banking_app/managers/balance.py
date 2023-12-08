from typing import Any
from typing import Type

from sqlalchemy import Insert
from sqlalchemy import Select
from sqlalchemy.orm import selectinload

from src.banking_app.managers.base import SeCrUpStmt
from src.banking_app.managers.base import SeCrUpManager
from src.banking_app.models.balance import Balance
from src.banking_app.models.client import Client


class BalanceManager(SeCrUpManager):

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

    def _enrich_statement(self, statement: SeCrUpStmt) -> SeCrUpStmt:
        """Enrich passed statement and return enriched statement."""

        if isinstance(statement, Insert):
            statement = (
                statement.
                options(
                    selectinload(self.model.client).
                    joinedload(Client.client_status)
                )
            )

        return statement
