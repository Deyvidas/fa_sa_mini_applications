from re import findall
from re import sub

from abc import ABC
from abc import abstractmethod

from typing import Any
from typing import Type
from typing import TypeVar

from sqlalchemy import delete
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import Select
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.dml import ReturningDelete
from sqlalchemy.sql.dml import ReturningInsert
from sqlalchemy.sql.dml import ReturningUpdate

from src.banking_app.conf import NotSpecifiedParam
from src.banking_app.models.base import Base
from src.banking_app.utils.kwargs_parser import KwargsParser


class AbstractManager(ABC):

    @property
    @abstractmethod
    def model(self) -> Type[Base]:
        ...


class AlterManager(AbstractManager):
    """Manager used to alter state in DB (create, update)."""

    def parse_integrity_error(self, error: IntegrityError) -> dict[str, Any]:
        """Parse IntegrityError message and return pairs key value."""

        parsed_strings = findall(r'\(.+\)=\(.+\)', error._message())
        keys_values = dict()
        for raw_string in parsed_strings:
            clean_string = sub(r'[\(\)]', '', raw_string)
            keys_values.update(eval(f'dict({clean_string})'))
        return keys_values


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


class CreateManager(AlterManager):

    def create(self, **kwargs) -> ReturningInsert:
        statement = (
            insert(self.model).
            values(**kwargs).
            returning(self.model)
        )
        return statement

    def bulk_create(self, list_kwargs: list[dict[str, Any]]) -> ReturningInsert:
        statement = (
            insert(self.model).
            values(list_kwargs).
            returning(self.model)
        )
        return statement


class UpdateManager(AlterManager):

    def update(
            self,
            *,
            where: dict[str, Any],
            set_value: dict[str, Any],
    ) -> ReturningUpdate:
        if len(set_value) == 0:
            raise ValueError(
                f'Without new values, updating can\'t proceed, {set_value=}.'
            )

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


class DeleteManager(AlterManager):

    def delete(self, **where) -> ReturningDelete:
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


AllStatements = TypeVar(
    'AllStatements',
    ReturningDelete,
    ReturningInsert,
    ReturningUpdate,
    Select,
)


class BaseManager(SelectManager,
                  CreateManager,
                  UpdateManager,
                  DeleteManager,):

    def _enrich_statement(self, statement: AllStatements) -> AllStatements:
        """Enrich passed statement and return enriched statement."""
        return statement


SeCrUpStmt = TypeVar(
    'SeCrUpStmt',
    ReturningInsert,
    ReturningUpdate,
    Select,
)


class SeCrUpManager(SelectManager,
                    CreateManager,
                    UpdateManager,):

    def _enrich_statement(self, statement: SeCrUpStmt) -> SeCrUpStmt:
        """Enrich passed statement and return enriched statement."""
        return statement
