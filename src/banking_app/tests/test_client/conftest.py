import pytest

from copy import deepcopy
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from typing import Any
from typing import Sequence
from typing import Type
from typing import TypeAlias

from src.banking_app.main import banking_app
from src.banking_app.managers.client import ClientManager
from src.banking_app.models.client import Client
from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.tests.helpers import BaseTest
from src.banking_app.tests.test_client.factory import factory_clients_dto


manager = ClientManager()
ClientData: TypeAlias = Client | BaseClientModel | dict[str, Any]


@pytest.mark.usefixtures('create_and_drop_tables')
class BaseTestClient(BaseTest):
    client = TestClient(banking_app)
    manager: ClientManager = manager
    model_dto: Type[BaseClientModel] = BaseClientModel
    model_orm: Type[Client] = Client
    ord_by_default = 'client_id'
    prefix = '/clients'

    def get_unexistent_client_id(self, objects: Sequence[ClientData]) -> int:
        return super().get_unexistent_numeric_value(field='client_id', objects=objects)


@pytest.fixture
def clients_dto_simple() -> Sequence[BaseClientModel]:
    """Fixture does't create statuses in the DB."""
    return deepcopy(factory_clients_dto)


@pytest.fixture
def clients_dto(statuses_orm, clients_dto_simple) -> Sequence[BaseClientModel]:
    """Fixture create statuses in the DB."""
    return clients_dto_simple


@pytest.fixture
def clients_orm(
        session: Session,
        clients_dto: Sequence[BaseClientModel],
) -> Sequence[Client]:
    exclude = set(BaseClientModel.model_fields.keys()) - set(BaseTestClient().fields)
    list_kwargs = [c.model_dump(exclude=exclude) for c in clients_dto]
    statement = manager.bulk_create(list_kwargs)
    instances = session.scalars(statement).unique().all()
    assert len(instances) == len(clients_dto)
    session.commit()

    return instances
