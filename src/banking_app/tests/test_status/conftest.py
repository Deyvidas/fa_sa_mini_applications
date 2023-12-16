import pytest

from fastapi.testclient import TestClient
from random import randint
from sqlalchemy.orm.session import Session

from typing import Any
from typing import Sequence
from typing import TypeAlias

from src.banking_app.main import banking_app
from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import Status
from src.banking_app.schemas.status import BaseStatusModel
from src.banking_app.tests.conftest import BaseTest


StatusData: TypeAlias = Status | BaseStatusModel | dict[str, Any]
manager = StatusManager()


@pytest.mark.usefixtures('create_and_drop_tables')
class BaseTestStatus(BaseTest):
    client = TestClient(banking_app)
    manager = manager
    model_orm = Status
    model_dto = BaseStatusModel
    prefix = '/status'
    ord_by_default = 'status'

    def get_unexistent_status_num(self, objects: Sequence[StatusData]) -> int:
        assert len(objects) > 0
        if isinstance(objects[0], dict):
            objects = [Status(**kwargs) for kwargs in objects]                  # type: ignore

        existent_statuses = [getattr(o, 'status') for o in objects]
        while True:
            num = randint(10 ** 5, 10 ** 6 - 1)  # [100_000; 999_999]
            if num not in existent_statuses:
                return num


@pytest.fixture()
def data_status() -> dict[str, Any]:
    """Fixture used into test_schemas."""
    random_status = generate_random_status(randint(1, 10 ** 9 - 1))
    return random_status.model_dump()


@pytest.fixture
def statuses_dto() -> Sequence[BaseStatusModel]:
    first = 100
    last = 900
    return [generate_random_status(i) for i in range(first, last + 1, 100)]


@pytest.fixture
def statuses_orm(
        session: Session,
        statuses_dto: list[BaseStatusModel],
) -> Sequence[Status]:
    list_kwargs = [status.model_dump() for status in statuses_dto]
    statement = manager.bulk_create(list_kwargs)
    instances = session.scalars(statement).unique().all()
    session.commit()

    assert len(instances) == len(statuses_dto)
    return instances


def generate_random_status(status_num: int = 100) -> BaseStatusModel:
    return BaseStatusModel(
        status=status_num,
        description=f'Test description {status_num}',
    )
