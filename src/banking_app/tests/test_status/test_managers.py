import pytest

from copy import deepcopy
from random import choice
from sqlalchemy.orm.session import Session

from typing import Sequence

from src.banking_app.models.status import Status
from src.banking_app.tests.general.managers import BaseTestBulkCreate
from src.banking_app.tests.general.managers import BaseTestCreate
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
class TestDelete(StatusTestHelper):

    def test_delete_status_with_status_number(
            self,
            session: Session,
            statuses_orm: Sequence[Status],
    ):
        count_before = len(statuses_orm)
        status_to_delete = choice(statuses_orm)

        # The deleted instance must be returned after delete.
        statement = self.manager.delete(status=status_to_delete.status)
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)
        self.compare_obj_before_after(status_to_delete, instance)

        # Ensure that the object is deleted from the DB.
        statement = self.manager.filter()
        instances: Sequence[Status] = session.scalars(statement).unique().all()
        assert len(instances) == count_before - 1

        found = list(filter(lambda i: i.status == status_to_delete.status, instances))
        assert len(found) == 0

    def test_delete_unexistent_status(
            self,
            session: Session,
            statuses_orm: Sequence[Status],
    ):
        statuses_before = deepcopy(statuses_orm)

        # Make an attempt to delete the status with an unexistent status_num.
        unexist_status_num = self.get_unexistent_status_num(statuses_orm)
        statement = self.manager.delete(status=unexist_status_num)
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 0

        # Ensure that the objects in the DB not been changed.
        statement = self.manager.filter()
        statuses_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(statuses_before, statuses_after)
