import pytest

from copy import deepcopy
from pydantic import TypeAdapter
from random import choice

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select

from typing import Sequence

from src.banking_app.models.status import Status
from src.banking_app.schemas.status import BaseStatusModel
from src.banking_app.tests.general.managers import BaseTestCreate
from src.banking_app.tests.test_status.factory import StatusFactory
from src.banking_app.tests.test_status.helpers import StatusTestHelper


@pytest.mark.run(order=1.00_00)
class TestCreate(StatusTestHelper, BaseTestCreate):
    ...


@pytest.mark.run(order=1.00_01)
class TestBulkCreate(StatusTestHelper):

    def test_base(
            self,
            session: Session,
            statuses_dto: Sequence[BaseStatusModel],
    ):
        list_kwargs = [self.get_orm_data_from_dto(s) for s in statuses_dto]

        # Test if bulk_create returns a list of created instances.
        statement = self.manager.bulk_create(list_kwargs)
        instances = session.scalars(statement).unique().all()
        session.commit()
        self.compare_list_before_after(list_kwargs, instances)

        # Check that objects have been created in the DB.
        statement = select(self.model_orm)
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(list_kwargs, instances_after)

    def test_with_some_not_unique(
            self,
            session: Session,
            statuses_dto: Sequence[BaseStatusModel]
    ):
        half = int(len(statuses_dto) / 2)

        # Saving the first part of having statuses.
        first_half = [self.get_orm_data_from_dto(s) for s in statuses_dto[:half]]
        statement = self.manager.bulk_create(first_half)
        instances = session.scalars(statement).unique().all()
        session.commit()

        # Try to create new statuses that are mixed with already existing statuses.
        second_half = [self.get_orm_data_from_dto(s) for s in statuses_dto[half:]]
        second_half += [first_half[0], first_half[-1]]
        statement = self.manager.bulk_create(second_half)
        with pytest.raises(IntegrityError) as error:
            session.execute(statement)
        kwargs = self.manager.parse_integrity_error(error.value)
        assert kwargs == {'status': first_half[0]['status']}

        # Check that there are no changes in the DB.
        session.rollback()
        statement = select(self.model_orm)
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(instances, instances_after)


@pytest.mark.run(order=1.00_02)
class TestFilter(StatusTestHelper):

    def test_without_arguments(
            self,
            session: Session,
            statuses_orm: Sequence[Status],
    ):
        # Check that filtering without parameters returns all objects from the DB.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        self.compare_list_before_after(statuses_orm, instances)

    def test_by_status_number(
            self,
            session: Session,
            statuses_orm: Sequence[Status]
    ):
        # Filtering by existent status number.
        existent_status = choice(statuses_orm)
        statement = self.manager.filter(status=existent_status.status)
        instance = session.scalars(statement).unique().all()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)
        self.compare_obj_before_after(existent_status, instance)

        # Filtering by unexistent status number.
        unexist_status = self.get_unexistent_status_num(statuses_orm)
        statement = self.manager.filter(status=unexist_status)
        instance = session.scalar(statement)
        assert instance is None


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
