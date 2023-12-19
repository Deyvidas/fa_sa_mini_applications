import pytest

from src.banking_app.tests.general.managers import BaseTestBulkCreate
from src.banking_app.tests.general.managers import BaseTestCreate
from src.banking_app.tests.general.managers import BaseTestDelete
from src.banking_app.tests.general.managers import BaseTestFilter
from src.banking_app.tests.general.managers import BaseTestUpdate
from src.banking_app.tests.test_status.helpers import StatusTestHelper


@pytest.mark.run(order=1.00_00)
class TestCreate(StatusTestHelper, BaseTestCreate):
    ...


@pytest.mark.run(order=1.00_01)
class TestBulkCreate(StatusTestHelper, BaseTestBulkCreate):
    ...


@pytest.mark.run(order=1.00_02)
class TestFilter(StatusTestHelper, BaseTestFilter):
    ...


@pytest.mark.run(order=1.00_03)
class TestUpdate(StatusTestHelper, BaseTestUpdate):
    ...


@pytest.mark.run(order=1.00_04)
class TestDelete(StatusTestHelper, BaseTestDelete):
    ...
