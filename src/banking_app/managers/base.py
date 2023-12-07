from abc import ABC
from abc import abstractmethod

from typing import Any
from typing import TypeVar

from sqlalchemy import Delete
from sqlalchemy import Select
from sqlalchemy import Insert
from sqlalchemy.sql.expression import delete
from sqlalchemy.sql.expression import insert
from sqlalchemy.sql.expression import select

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


class DeleteManager(AbstractManager):

    def delete(self, **kwargs: dict[str, Any]) -> Delete:
        statement = (
            delete(self.model).
            filter_by(**kwargs).
            returning(self.model)
        )
        return statement


AllStatements = TypeVar('AllStatements', Delete, Select, Insert)


class BaseManager(SelectManager,
                  CreateManager,
                  DeleteManager):

    def _enrich_statement(self, statement: AllStatements) -> AllStatements:
        """Enrich passed statement and return enriched statement."""
        return statement


SelCreStmt = TypeVar('SelCreStmt', Select, Insert)


class SelectCreateManager(SelectManager,
                          CreateManager,):

    def _enrich_statement(self, statement: SelCreStmt) -> SelCreStmt:
        """Enrich passed statement and return enriched statement."""
        return statement
