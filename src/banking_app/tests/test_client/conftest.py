import pytest

from copy import deepcopy
from typing import Sequence

from src.banking_app.models.client import Client
from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.tests.test_client.factory import factory_clients_dto
from src.banking_app.tests.test_client.helpers import ClientTestHelper
from src.banking_app.tests.test_client.helpers import manager


@pytest.fixture
def clients_dto_simple() -> Sequence[BaseClientModel]:
    return deepcopy(factory_clients_dto)


@pytest.fixture
def clients_dto(statuses_orm, clients_dto_simple) -> Sequence[BaseClientModel]:
    """Fixture create statuses in the DB."""
    return clients_dto_simple


@pytest.fixture
def clients_orm(session, clients_dto) -> Sequence[Client]:
    exclude = set(BaseClientModel.model_fields.keys()) - set(ClientTestHelper().fields)
    list_kwargs = [c.model_dump(exclude=exclude) for c in clients_dto]
    statement = manager.bulk_create(list_kwargs)
    instances = session.scalars(statement).unique().all()
    assert len(instances) == len(clients_dto)
    session.commit()

    return instances
