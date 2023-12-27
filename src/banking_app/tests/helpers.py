from abc import ABC
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory

from pydantic import BaseModel
from pydantic import TypeAdapter

from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import delete

from typing import Any
from typing import Callable
from typing import Sequence
from typing import TypeAlias

from src.banking_app.managers.base import BaseManager
from src.banking_app.models.base import Base


class BaseTestHelper(ABC):
    client: TestClient
    factory: ModelFactory
    manager: BaseManager
    model_dto: type[BaseModel]
    model_orm: type[Base]
    prefix: str

    DataType: TypeAlias = Base | BaseModel | dict[str, Any]

    @property
    def fields(self) -> set[str]:
        fields = self.model_orm.__mapper__.column_attrs
        return set(f.key for f in fields)

    @property
    def related_fields(self) -> set[str]:
        related_fields = self.model_orm.__mapper__.relationships
        return set(rf.key for rf in related_fields)

    @property
    def fields_excluded(self) -> set[str]:
        dto_excluded = set()
        for f, obj in self.model_dto.model_fields.items():
            if obj.exclude is True:
                dto_excluded.add(f)
        return dto_excluded

    @property
    def primary_keys(self) -> set[str]:
        primary_keys = self.model_orm.__mapper__.primary_key
        return set(f.key for f in primary_keys)

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

    @property
    def get_dto_from_single(self) -> Callable:
        return TypeAdapter(self.model_dto).validate_python

    @property
    def get_dto_from_many(self) -> Callable:
        return TypeAdapter(list[self.model_dto]).validate_python

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

    def refresh_dto_model[T: BaseModel](self, session: Session, model: T) -> T:
        dto_model = type(model)
        data = TypeAdapter(dto_model).dump_python(model, include=self.fields)
        [data.setdefault(f, v) for f, v in self.default_values.items()]

        # Drop all - to save original (not incremented) PK values.
        session.execute(delete(self.model_orm))
        instance = self.model_orm(**data)
        session.add(instance)
        session.flush()

        model = TypeAdapter(dto_model).validate_python(instance)
        session.rollback()
        return model

    def get_orm_data_from_dto(
            self,
            dto_model: BaseModel,
            *,
            exclude: set[str] | None = None,
    ) -> dict[str, Any]:
        return TypeAdapter(self.model_dto).dump_python(
            dto_model,
            include=self.fields,
            exclude=exclude,
        )

    def get_unexistent_numeric_value(
            self,
            field: str,
            objects: Sequence[DataType],
    ) -> int:
        assert len(objects) > 0
        sorted_numbers = sorted(getattr(o, field) for o in objects)
        return sorted_numbers[-1] + 1

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
        if not isinstance(before[0], self.model_dto):
            before = self.get_dto_from_many(before)
        if not isinstance(after[0], self.model_dto):
            after = self.get_dto_from_many(after)

        fields = self._get_final_field_set(exclude, fields)
        sortable = set(fields) & self._get_sortable_fields()

        if len(before) > 1:
            before = sorted(before, key=lambda b: [getattr(b, s) for s in sortable])
            after = sorted(after, key=lambda a: [getattr(a, s) for s in sortable])

        for b, a in zip(before, after):
            for field in fields:
                assert getattr(a, field) == getattr(b, field)

    def _get_sortable_fields(self) -> set[str]:
        sortable = set()
        for f, obj in self.model_dto.model_fields.items():
            if '__lt__' in dir(obj.annotation):
                sortable.add(f)
        return sortable - self.related_fields

    def _get_final_field_set[S: Sequence[str]](
            self,
            exclude: S | None,
            fields: S | None,
    ) -> S:
        _fields = (self.fields | self.related_fields) - self.fields_excluded
        if fields is not None and len(fields) > 0:
            _fields = fields
        if exclude is not None and len(exclude) > 0:
            diff = set(_fields) - set(exclude)
            if len(diff) != 0:
                return list(diff)                                               # type: ignore
        return list(_fields)                                                    # type: ignore
