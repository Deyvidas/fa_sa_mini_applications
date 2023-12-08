from abc import ABC
from abc import abstractmethod

from typing import Any
from typing import TypeVar

from sqlalchemy import delete
from sqlalchemy import Delete
from sqlalchemy import insert
from sqlalchemy import Insert
from sqlalchemy import select
from sqlalchemy import Select
from sqlalchemy import update
from sqlalchemy import Update

from src.banking_app.conf import NotSpecifiedParam
from src.banking_app.models.base import Base
from src.banking_app.utils.kwargs_parser import KwargsParser


class AbstractManager(ABC):

    @property
    @abstractmethod
    def model(self) -> Base: ...


class SelectManager(AbstractManager):

    def filter(self, **kwargs) -> Select:
        self._remove_not_specified_params(kwargs)
        conditions = KwargsParser().parse_kwargs(
            module_name=__name__,
            model=self.model,
            **kwargs,
        )
        statement = (
            select(self.model).
            where(*eval(conditions))
        )
        return statement

    @staticmethod
    def _remove_not_specified_params(kwargs: dict[str, Any]) -> None:
        """Pop from dictionary keys which value has NotSpecifiedParam type."""
        keys_to_pop = [k for k, v in kwargs.items() if v is NotSpecifiedParam]
        [kwargs.pop(key) for key in keys_to_pop]


class CreateManager(AbstractManager):

    def create(self, **kwargs) -> Insert:
        statement = (
            insert(self.model).
            values(**kwargs).
            returning(self.model)
        )
        return statement

    def bulk_create(self, list_kwargs: list[dict[str, Any]]) -> Insert:
        statement = (
            insert(self.model).
            values(list_kwargs).
            returning(self.model)
        )
        return statement


class UpdateManager(AbstractManager):

    def update(
            self,
            *,
            where: dict[str, Any],
            set_value: dict[str, Any],
    ) -> Update:
        conditions = KwargsParser().parse_kwargs(
            module_name=__name__,
            model=self.model,
            **where,
        )
        statement = (
            update(self.model).
            where(*eval(conditions)).
            values(**set_value).
            returning(self.model)
        )
        return statement


class DeleteManager(AbstractManager):

    def delete(self, **where) -> Delete:
        conditions = KwargsParser().parse_kwargs(
            module_name=__name__,
            model=self.model,
            **where,
        )
        statement = (
            delete(self.model).
            where(*eval(conditions)).
            returning(self.model)
        )
        return statement


AllStatements = TypeVar('AllStatements', Delete, Select, Insert, Update)


class BaseManager(SelectManager,
                  CreateManager,
                  UpdateManager,
                  DeleteManager,):

    def _enrich_statement(self, statement: AllStatements) -> AllStatements:
        """Enrich passed statement and return enriched statement."""
        return statement


SeCrUpStmt = TypeVar('SeCrUpStmt', Select, Insert, Update)


class SeCrUpManager(SelectManager,
                    CreateManager,
                    UpdateManager,):

    def _enrich_statement(self, statement: SeCrUpStmt) -> SeCrUpStmt:
        """Enrich passed statement and return enriched statement."""
        return statement
