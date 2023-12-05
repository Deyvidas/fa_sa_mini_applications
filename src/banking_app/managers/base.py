from abc import ABC
from abc import abstractmethod

from typing import Any

from sqlalchemy import Select
from sqlalchemy import Insert
from sqlalchemy.sql.expression import insert
from sqlalchemy.sql.expression import select

from src.banking_app.conf import NotSpecifiedParam
from src.banking_app.models.base import Base


class AbstractManager(ABC):

    @property
    @abstractmethod
    def model(self) -> Base: ...


class BaseManager(AbstractManager):

    def filter(self, **kwargs) -> Select:
        self._remove_not_specified_params(kwargs)
        statement = select(self.model).filter_by(**kwargs)
        return statement

    def create(self, **kwargs) -> Insert:
        statement = (
            insert(self.model)
            .values(**kwargs)
            .returning(self.model)
        )
        return statement

    def bulk_create(self, list_kwargs: list[dict[str, Any]]) -> Insert:
        statement = (
            insert(self.model)
            .values(list_kwargs)
            .returning(self.model)
        )
        return statement

    @staticmethod
    def _remove_not_specified_params(kwargs: dict[str, Any]) -> None:
        """Pop from dictionary keys which value has NotSpecifiedParam type."""
        keys_to_pop = [k for k, v in kwargs.items() if v is NotSpecifiedParam]
        [kwargs.pop(key) for key in keys_to_pop]
