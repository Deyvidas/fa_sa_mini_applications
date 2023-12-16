import pytest

from fastapi.testclient import TestClient

from random import randint
from sqlalchemy.orm.session import Session

from typing import Any
from typing import Sequence
from typing import TypeAlias

from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import Status
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.main import banking_app


manager = StatusManager()
StatusData: TypeAlias = Status | StatusRetrieve | dict[str, Any]


@pytest.mark.usefixtures('create_and_drop_tables')
class BaseTestStatus:
    client = TestClient(banking_app)
    manager = manager
    model = Status
    prefix = '/status'

    not_found_msg = '{} with status={} not found.'
    not_unique_msg = '{} with status={} already exists.'
    empty_patch_body = '{} with status={} can\'t be updated, received empty body, change at least value of one field.'

    @property
    def fields(self) -> Sequence[str]:
        fields = self.model.__table__.columns._all_columns
        return [field.name for field in fields]

    def get_unexistent_status_num(self, objects: Sequence[StatusData]) -> int:
        assert len(objects) > 0
        objects = self.list_of_dict_to_orm(objects)
        existent_statuses = [getattr(o, 'status') for o in objects]
        while True:
            num = randint(10 ** 5, 10 ** 6 - 1)  # [100_000; 999_999]
            if num not in existent_statuses:
                return num

    def compare_list_before_after[T: StatusData, S: Sequence[str]](
            self,
            before: Sequence[T],
            after: Sequence[T],
            *,
            exclude: S | None = None,
            fields: S | None = None,
    ):
        assert len(before) == len(after)
        before = self.list_of_dict_to_orm(before)
        after = self.list_of_dict_to_orm(after)

        # By default we sort by status, but it can be excluded, than take first field.
        fields = self._get_final_field_set(exclude, fields)
        ord_by = 'status'
        if ord_by not in fields:
            ord_by = fields[0]

        before_ord = sorted(before, key=lambda b: getattr(b, ord_by))
        after_ord = sorted(after, key=lambda a: getattr(a, ord_by))
        for b, a in zip(before_ord, after_ord):
            self.compare_obj_before_after(b, a, exclude=exclude, fields=fields)

    def compare_obj_before_after[T: StatusData, S: Sequence[str]](
            self,
            before: T,
            after: T,
            *,
            exclude: S | None = None,
            fields: S | None = None,
    ):
        before = self.list_of_dict_to_orm([before])[0]
        after = self.list_of_dict_to_orm([after])[0]

        fields = self._get_final_field_set(exclude, fields)
        for field in fields:
            assert getattr(after, field) == getattr(before, field)

    def list_of_dict_to_orm[T: Sequence[StatusData]](self, objects: T) -> T:
        list_of_dicts = all(map(lambda o: isinstance(o, dict), objects))
        if list_of_dicts:
            return [Status(**object) for object in objects]                     # type: ignore
        return objects

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


@pytest.fixture()
def data_status():
    """Fixture used into test_schemas."""
    default_data = dict(
        status=100,
        description='Test description',
    )
    return default_data


@pytest.fixture
def statuses_dto() -> Sequence[StatusRetrieve]:
    first = 100
    last = 900

    statuses: list[StatusRetrieve] = list()
    for i in range(first, last + 1, 100):
        status = StatusRetrieve(
            status=i,
            description=f'Test description {i}',
        )
        statuses.append(status)

    return statuses


@pytest.fixture
def statuses_orm(
        session: Session,
        statuses_dto: list[StatusRetrieve],
) -> Sequence[Status]:
    list_kwargs = [status.model_dump() for status in statuses_dto]
    statement = manager.bulk_create(list_kwargs)
    instances = session.scalars(statement).unique().all()
    session.commit()

    assert len(instances) == len(statuses_dto)
    return instances
