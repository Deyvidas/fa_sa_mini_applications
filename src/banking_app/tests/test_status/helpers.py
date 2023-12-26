import pytest

from fastapi.testclient import TestClient

from typing import Any
from typing import Sequence
from typing import TypeAlias

from src.banking_app.main import banking_app
from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import Status
from src.banking_app.schemas import StatusModelWithRelations
from src.banking_app.tests.helpers import BaseTestHelper
from src.banking_app.tests.test_status.factory import StatusFactory


StatusData: TypeAlias = Status | StatusModelWithRelations | dict[str, Any]
manager = StatusManager()


@pytest.mark.usefixtures('create_and_drop_tables')
class StatusTestHelper(BaseTestHelper):
    client = TestClient(banking_app)
    factory: StatusFactory = StatusFactory()
    manager: StatusManager = manager
    model_dto: type[StatusModelWithRelations] = StatusModelWithRelations
    model_orm: type[Status] = Status
    prefix = '/status'

    @pytest.fixture
    def models_dto(self, statuses_dto) -> Sequence[StatusModelWithRelations]:
        return statuses_dto

    @pytest.fixture
    def models_orm(self, statuses_orm) -> Sequence[Status]:
        return statuses_orm

    def get_unexistent_status_num(self, objects: Sequence[StatusData]) -> int:
        return super().get_unexistent_numeric_value(field='status', objects=objects)
