import pytest

from copy import deepcopy
from typing import Sequence

from src.banking_app.models.status import Status
from src.banking_app.schemas import StatusModelWithRelations
from src.banking_app.tests.test_status.factory import factory_statuses_dto
from src.banking_app.tests.test_status.helpers import manager
from src.banking_app.tests.test_status.helpers import StatusTestHelper


get_orm_data_from_dto = StatusTestHelper().get_orm_data_from_dto


@pytest.fixture
def statuses_dto() -> Sequence[StatusModelWithRelations]:
    return deepcopy(factory_statuses_dto)


@pytest.fixture
def statuses_orm(session, statuses_dto) -> Sequence[Status]:
    list_kwargs = [get_orm_data_from_dto(status) for status in statuses_dto]
    statement = manager.bulk_create(list_kwargs)
    instances = session.scalars(statement).unique().all()
    assert len(instances) == len(statuses_dto)

    session.commit()
    return instances
