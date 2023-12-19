import pytest

from src.banking_app.tests.general.managers import BaseTestBulkCreate
from src.banking_app.tests.general.managers import BaseTestCreate
from src.banking_app.tests.general.managers import BaseTestDelete
from src.banking_app.tests.general.managers import BaseTestFilter
from src.banking_app.tests.general.managers import BaseTestUpdate
from src.banking_app.tests.test_client.conftest import ClientTestHelper


@pytest.mark.run(order=1.01_00)
class TestCreate(ClientTestHelper, BaseTestCreate):
    ...


@pytest.mark.run(order=1.01_01)
class TestBulkCreate(ClientTestHelper, BaseTestBulkCreate):
    ...


@pytest.mark.run(order=1.01_02)
class TestFilter(ClientTestHelper, BaseTestFilter):
    ...


@pytest.mark.run(order=1.01_03)
class TestUpdate(ClientTestHelper, BaseTestUpdate):
    ...


@pytest.mark.run(order=1.01_04)
class TestDelete(ClientTestHelper, BaseTestDelete):
    ...
