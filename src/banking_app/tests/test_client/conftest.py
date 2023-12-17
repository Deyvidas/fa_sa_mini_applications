import pytest

from copy import deepcopy
from fastapi.testclient import TestClient
from typing import Any
from typing import Sequence

from src.banking_app.main import banking_app
from src.banking_app.managers.client import ClientManager
from src.banking_app.models.client import Client
from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.tests.helpers import BaseTest
from src.banking_app.tests.test_client.factory import factory_clients_dto


@pytest.mark.usefixtures('create_and_drop_tables')
class BaseTestClient(BaseTest):
    client = TestClient(banking_app)
    manager = ClientManager()
    model_dto = BaseClientModel
    model_orm = Client
    ord_by_default = 'client_id'
    prefix = '/clients'

    def get_required_values(self, model_dto: BaseClientModel) -> dict[str, Any]:
        return {field: getattr(model_dto, field) for field in self.fields}


@pytest.fixture
def clients_dto_simple() -> Sequence[BaseClientModel]:
    """Fixture does't create statuses in the DB."""
    return deepcopy(factory_clients_dto)


@pytest.fixture
def clients_dto(statuses_orm, clients_dto_simple) -> Sequence[BaseClientModel]:
    """Fixture create statuses in the DB."""
    return clients_dto_simple
