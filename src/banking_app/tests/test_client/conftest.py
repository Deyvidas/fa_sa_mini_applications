import pytest

from copy import deepcopy
from typing import Sequence

from src.banking_app.models.client import Client
from src.banking_app.schemas import ClientModelWithRelations
from src.banking_app.tests.test_client.factory import factory_clients_dto
from src.banking_app.tests.test_client.helpers import ClientTestHelper
from src.banking_app.tests.test_client.helpers import manager


get_orm_data_from_dto = ClientTestHelper().get_orm_data_from_dto


@pytest.fixture
def clients_dto_simple() -> Sequence[ClientModelWithRelations]:
    return deepcopy(factory_clients_dto)


@pytest.fixture
def clients_dto(statuses_orm, clients_dto_simple) -> Sequence[ClientModelWithRelations]:
    """Fixture create statuses in the DB."""
    return clients_dto_simple


@pytest.fixture
def clients_orm(session, clients_dto) -> Sequence[Client]:
    list_kwargs = [get_orm_data_from_dto(c) for c in clients_dto]
    statement = manager.bulk_create(list_kwargs)
    instances = session.scalars(statement).unique().all()
    assert len(instances) == len(clients_dto)
    session.commit()

    return instances
