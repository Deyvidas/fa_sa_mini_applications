from sqlalchemy import Select
from sqlalchemy.sql.dml import ReturningDelete
from sqlalchemy.sql.dml import ReturningInsert

from typing import Any

from src.banking_app.managers.base import AllStatements
from src.banking_app.managers.base import BaseManager
from src.banking_app.models.client import Client


class ClientManager(BaseManager):
    model: type[Client] = Client

    def filter(self, **kwargs) -> Select:
        statement = self._enrich_statement(super().filter(**kwargs))
        return statement

    def create(self, **kwargs) -> ReturningInsert:
        statement = self._enrich_statement(super().create(**kwargs))
        return statement

    def bulk_create(self, list_kwargs: list[dict[str, Any]]) -> ReturningInsert:
        statement = self._enrich_statement(super().bulk_create(list_kwargs))
        return statement

    def delete(self, **kwargs) -> ReturningDelete:
        statement = self._enrich_statement(super().delete(**kwargs))
        return statement

    def _enrich_statement(self, statement: AllStatements) -> AllStatements:
        """Enrich passed statement and return enriched statement."""

        if isinstance(statement, Select):
            statement = (
                statement.
                order_by(self.model.reg_date.desc()).
                order_by(self.model.full_name.asc())
            )

        return statement
