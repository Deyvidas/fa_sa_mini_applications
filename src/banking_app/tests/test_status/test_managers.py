import pytest

from copy import deepcopy
from pydantic import TypeAdapter
from random import choice
from sqlalchemy.orm.session import Session

from typing import Sequence

from src.banking_app.models.status import Status
from src.banking_app.tests.general.managers import BaseTestBulkCreate
from src.banking_app.tests.general.managers import BaseTestCreate
from src.banking_app.tests.general.managers import BaseTestFilter
from src.banking_app.tests.test_status.factory import StatusFactory
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
class TestUpdate(StatusTestHelper):
    AdapterOne = TypeAdapter(StatusTestHelper.model_dto).validate_python

    def test_update_single_status_with_status_num(
            self,
            session: Session,
            statuses_orm: Sequence[Status],
    ):
        status_to_update = choice(statuses_orm)

        # Prepare data.
        new_status_dto = StatusFactory().build(factory_use_construct=True)
        while self.AdapterOne(status_to_update) == new_status_dto:
            status_to_update = choice(statuses_orm)
        status_to_update = deepcopy(status_to_update)  # To save original state.
        new_data = self.get_orm_data_from_dto(new_status_dto, exclude={'status'})

        # Update must change single status and return it with updated field values.
        statement = self.manager.update(
            where=dict(status=status_to_update.status),
            set_value=new_data,
        )
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)

        # Check that the updated status has been returned with updated fields.
        new_data['status'] = status_to_update.status
        self.compare_obj_before_after(new_data, instance)

        # Ensure that the object has new values in the DB.
        statement = self.manager.filter(status=status_to_update.status)
        instance_after = session.scalars(statement).unique().all()
        assert len(instance_after) == 1
        assert isinstance(instance_after := instance_after[0], self.model_orm)
        self.compare_obj_before_after(instance, instance_after)

    def test_update_unexistent_status(
            self,
            session: Session,
            statuses_orm: Sequence[Status],
    ):
        statuses_before = deepcopy(statuses_orm)

        # Make an attempt to update the status with an unexistent status_num.
        unexist_status_num = self.get_unexistent_status_num(statuses_orm)
        statement = self.manager.update(
            where=dict(status=unexist_status_num),
            set_value=dict(description='Description for unexistent status.'),
        )
        instances = session.scalars(statement).unique().all()
        session.commit()
        assert len(instances) == 0

        # Ensure that the objects in the DB not been changed.
        statement = self.manager.filter()
        statuses_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(statuses_before, statuses_after)

    def test_update_without_new_values(self, statuses_orm: Sequence[Status]):
        # Make an attempt to create statement without values.
        status = choice(statuses_orm).status
        with pytest.raises(ValueError) as error:
            self.manager.update(where=dict(status=status), set_value=dict())
        msg = 'Without new values, updating can\'t proceed, set_value={}.'
        assert str(error.value) == msg


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
