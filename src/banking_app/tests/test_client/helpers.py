import pytest

from fastapi.testclient import TestClient

from typing import Any
from typing import Sequence
from typing import Type
from typing import TypeAlias

from src.banking_app.main import banking_app
from src.banking_app.managers.client import ClientManager
from src.banking_app.models.client import Client
from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.tests.helpers import BaseTestHelper


ClientData: TypeAlias = Client | BaseClientModel | dict[str, Any]
manager = ClientManager()


@pytest.mark.usefixtures('create_and_drop_tables')
class ClientTestHelper(BaseTestHelper):
    client = TestClient(banking_app)
    manager: ClientManager = manager
    model_dto: Type[BaseClientModel] = BaseClientModel
    model_orm: Type[Client] = Client
    prefix = '/clients'

    @pytest.fixture
    def models_dto(self, clients_dto) -> Sequence[BaseClientModel]:
        return clients_dto

    @pytest.fixture
    def models_orm(self, clients_orm) -> Sequence[Client]:
        return clients_orm

    def get_unexistent_client_id(self, objects: Sequence[ClientData]) -> int:
        return super().get_unexistent_numeric_value(field='client_id', objects=objects)
