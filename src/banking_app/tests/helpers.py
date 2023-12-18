from abc import ABC
from fastapi.testclient import TestClient
from pydantic import BaseModel
from random import randint

from typing import Any
from typing import Sequence
from typing import Type
from typing import TypeAlias

from src.banking_app.managers.base import BaseManager
from src.banking_app.models.base import Base


class BaseTestHelper(ABC):
    client: TestClient
    manager: BaseManager
    model_dto: Type[BaseModel]
    model_orm: Type[Base]
    prefix: str

    DataType: TypeAlias = Base | BaseModel | dict[str, Any]

    @property
    def fields(self) -> Sequence[str]:
        fields = self.model_orm.__table__.columns._all_columns
        return [field.name for field in fields]

    @property
    def primary_keys(self) -> set[str]:
        fields = [getattr(self.model_orm, f) for f in self.fields]
        return set(f.name for f in fields if f.primary_key is True)

    @property
    def default_values(self) -> dict[str, Any]:
        defaults = dict()
        for field in self.fields:
            value = getattr(self.model_orm, field).default
            if value is None:
                continue
            value = value.arg
            if callable(value):
                value = value(None)
            defaults[field] = value
        return defaults

    def not_found_msg(self, **kwargs) -> str:
        details = ', '.join([f'{k}={v}' for k, v in kwargs.items()])
        return f'{self.model_orm.__name__} with {details} not found.'

    def not_unique_msg(self, **kwargs) -> str:
        details = ', '.join([f'{k}={v}' for k, v in kwargs.items()])
        return f'{self.model_orm.__name__} with {details} already exists.'

    def empty_patch_body(self, **kwargs) -> str:
        details = ', '.join([f'{k}={v}' for k, v in kwargs.items()])
        return (
            f'{self.model_orm.__name__} with {details} can\'t be updated,'
            ' received empty body, change at least value of one field.'
        )

    def get_orm_data_from_dto(
            self,
            dto_model: BaseModel,
            *,
            exclude: set[str] | None = None,
    ) -> dict[str, Any]:
        _exclude = set(self.model_dto.model_fields.keys()) - set(self.fields)
        if exclude is not None:
            _exclude = _exclude.union(exclude)
        return dto_model.model_dump(exclude=_exclude)

    def get_unexistent_numeric_value(
            self,
            *,
            field: str,
            objects: Sequence[DataType],
    ) -> int:
        assert len(objects) > 0
        if all(map(lambda o: isinstance(o, dict), objects)):
            objects = [self.model_orm(**kwargs) for kwargs in objects]          # type: ignore

        existent_numbers = [getattr(o, field) for o in objects]
        while True:
            num = randint(10 ** 5, 10 ** 6 - 1)  # [100_000; 999_999]
            if num not in existent_numbers:
                return num

    def compare_obj_before_after[T: DataType, S: Sequence[str]](
            self,
            before: T,
            after: T,
            *,
            exclude: S | None = None,
            fields: S | None = None,
    ):
        self.compare_list_before_after(
            before=[before],
            after=[after],
            exclude=exclude,
            fields=fields,
        )

    def compare_list_before_after[T: DataType, S: Sequence[str]](
            self,
            before: Sequence[T],
            after: Sequence[T],
            *,
            exclude: S | None = None,
            fields: S | None = None,
    ):
        assert len(before) == len(after) and len(before) > 0

        # Convert dict into an instance to use getattr.
        if isinstance(before[0], dict):
            before = [self.model_orm(**kwargs) for kwargs in before]            # type: ignore
        if isinstance(after[0], dict):
            after = [self.model_orm(**kwargs) for kwargs in after]              # type: ignore

        fields = self._get_final_field_set(exclude, fields)
        # By default we sort by primary key, but it can be excluded.
        ord_by = list(self.primary_keys)[0]
        if ord_by not in fields:
            ord_by = fields[0]

        if len(before) > 1:
            before = sorted(before, key=lambda b: getattr(b, ord_by))
            after = sorted(after, key=lambda a: getattr(a, ord_by))

        for b, a in zip(before, after):
            for field in fields:
                assert getattr(a, field) == getattr(b, field)

    def _get_final_field_set[S: Sequence[str]](
            self,
            exclude: S | None,
            fields: S | None,
    ) -> S:
        _fields = self.fields
        if fields is not None and len(fields) > 0:
            _fields = fields
        if exclude is not None and len(exclude) > 0:
            diff = set(_fields) - set(exclude)
            if len(diff) != 0:
                return list(diff)                                               # type: ignore
        return list(_fields)                                                    # type: ignore
