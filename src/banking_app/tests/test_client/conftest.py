import pytest

from copy import deepcopy
from fastapi.testclient import TestClient
from typing import Sequence

from src.banking_app.main import banking_app
from src.banking_app.managers.client import ClientManager
from src.banking_app.models.client import Client
from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.tests.conftest import BaseTest
from src.banking_app.tests.test_client.factory import factory_clients_dto


@pytest.mark.usefixtures('create_and_drop_tables')
class BaseTestClient(BaseTest):
    client = TestClient(banking_app)
    manager = ClientManager()
    model_dto = BaseClientModel
    model_orm = Client
    ord_by_default = 'client_id'
    prefix = '/clients'


@pytest.fixture
def clients_dto() -> Sequence[BaseClientModel]:
    return deepcopy(factory_clients_dto)
