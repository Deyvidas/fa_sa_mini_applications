import pytest

from copy import deepcopy
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from typing import Any
from typing import Sequence
from typing import Type
from typing import TypeAlias

from src.banking_app.main import banking_app
from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import Status
from src.banking_app.schemas.status import BaseStatusModel
from src.banking_app.tests.helpers import BaseTest
from src.banking_app.tests.test_status.factory import factory_statuses_dto


StatusData: TypeAlias = Status | BaseStatusModel | dict[str, Any]
manager = StatusManager()


@pytest.mark.usefixtures('create_and_drop_tables')
class BaseTestStatus(BaseTest):
    client = TestClient(banking_app)
    manager: StatusManager = manager
    model_orm: Type[Status] = Status
    model_dto: Type[BaseStatusModel] = BaseStatusModel
    prefix = '/status'
    ord_by_default = 'status'

    def get_unexistent_status_num(self, objects: Sequence[StatusData]) -> int:
        return super().get_unexistent_numeric_value(field='status', objects=objects)


@pytest.fixture
def statuses_dto() -> Sequence[BaseStatusModel]:
    return deepcopy(factory_statuses_dto)


@pytest.fixture
def statuses_orm(
        session: Session,
        statuses_dto: Sequence[BaseStatusModel],
) -> Sequence[Status]:
    list_kwargs = [status.model_dump() for status in statuses_dto]
    statement = manager.bulk_create(list_kwargs)
    instances = session.scalars(statement).unique().all()
    session.commit()

    assert len(instances) == len(statuses_dto)
    return instances
