import pytest

from src.banking_app.schemas import ClientCreate
from src.banking_app.schemas import ClientRetrieve
from src.banking_app.tests.general.endpoints import BaseTestPost
from src.banking_app.tests.general.endpoints import BaseTestRetrieve
from src.banking_app.tests.test_client.helpers import ClientTestHelper


@pytest.mark.run(order=2.01_00)
class TestRetrieve(ClientTestHelper, BaseTestRetrieve):
    model_dto = ClientRetrieve


@pytest.mark.run(order=2.01_01)
class TestPost(ClientTestHelper, BaseTestPost):
    model_dto = ClientRetrieve
    model_dto_post = ClientCreate
