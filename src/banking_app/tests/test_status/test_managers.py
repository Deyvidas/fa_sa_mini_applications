import pytest

from copy import deepcopy
from random import choice

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select

from typing import Sequence

from src.banking_app.models.status import Status
from src.banking_app.schemas.status import BaseStatusModel
from src.banking_app.tests.test_status.conftest import BaseTestStatus


@pytest.mark.run(order=1.00_00)
class TestCreate(BaseTestStatus):

    def test_base(
            self,
            session: Session,
            statuses_dto: Sequence[BaseStatusModel],
    ):
        status_dto = choice(statuses_dto)

        # Test that create returns the created instance.
        statement = self.manager.create(**status_dto.model_dump())
        instances = session.scalars(statement).unique().all()
        session.commit()
        assert len(instances) == 1
        self.compare_obj_before_after(status_dto, instances[0])

        # Check that the object has been created in the DB.
        statement = select(self.model_orm)
        instances_after = session.scalars(statement).unique().all()
        assert len(instances_after) == 1
        self.compare_obj_before_after(instances[0], instances_after[0])

    def test_not_unique(
            self,
            session: Session,
            statuses_dto: Sequence[BaseStatusModel],
    ):
        status_dto = choice(statuses_dto)

        # Create instance of status in DB.
        statement = self.manager.create(**status_dto.model_dump())
        instance = session.scalar(statement)
        session.commit()
        assert isinstance(instance, Status)

        # Try to create another status object with same fields values.
        statement = self.manager.create(**status_dto.model_dump())
        with pytest.raises(IntegrityError) as error:
            session.scalar(statement)
        kwargs = self.manager.parse_integrity_error(error.value)
        assert kwargs == {'status': status_dto.status}

        # Check that there are no changes in the DB.
        session.rollback()
        statement = select(self.model_orm)
        instances = session.scalars(statement).unique().all()
        assert len(instances) == 1
        self.compare_obj_before_after(instance, instances[0])


@pytest.mark.run(order=1.00_01)
class TestBulkCreate(BaseTestStatus):

    def test_base(
            self,
            session: Session,
            statuses_dto: Sequence[BaseStatusModel],
    ):
        list_kwargs = [s.model_dump() for s in statuses_dto]

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
        first_half = [s.model_dump() for s in statuses_dto[:half]]
        statement = self.manager.bulk_create(first_half)
        instances = session.scalars(statement).unique().all()
        session.commit()

        # Try to create new statuses that are mixed with already existing statuses.
        second_half = [s.model_dump() for s in statuses_dto[half:]]
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
class TestFilter(BaseTestStatus):

    def test_without_arguments(
            self,
            session: Session,
            statuses_orm: list[Status],
    ):
        # Check that filtering without parameters returns all objects from the DB.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        self.compare_list_before_after(statuses_orm, instances)

    def test_by_status_number(
            self,
            session: Session,
            statuses_orm: list[Status]
    ):
        # Filtering by existent status number.
        existent_status = choice(statuses_orm)
        statement = self.manager.filter(status=existent_status.status)
        instance = session.scalar(statement)
        assert isinstance(instance, Status)
        self.compare_obj_before_after(existent_status, instance)

        # Filtering by unexistent status number.
        unexist_status = self.get_unexistent_status_num(statuses_orm)
        statement = self.manager.filter(status=unexist_status)
        instance = session.scalar(statement)
        assert instance is None


@pytest.mark.run(order=1.00_03)
class TestUpdate(BaseTestStatus):

    def test_update_single_status_with_status_num(
            self,
            session: Session,
            statuses_orm: list[Status],
    ):
        status_to_update = choice(statuses_orm)

        # Update must change single status and return it with updated field values.
        new_description = status_to_update.description + '(updated)'
        statement = self.manager.update(
            where=dict(status=status_to_update.status),
            set_value=dict(description=new_description),
        )
        instances = session.scalars(statement).unique().all()
        session.commit()
        assert len(instances) == 1

        # Check the new value of description field.
        instance = instances[0]
        assert isinstance(instance, Status)
        assert instance.description == new_description
        self.compare_obj_before_after(
            status_to_update,
            instance,
            exclude=['description'],
        )

        # Ensure that the object has new values in the DB.
        statement = self.manager.filter(status=instance.status)
        instance_after = session.scalars(statement).unique().all()
        assert len(instance_after) == 1 and isinstance(instance_after[0], Status)
        assert instance_after[0].description == new_description
        self.compare_obj_before_after(
            status_to_update,
            instance_after[0],
            exclude=['description'],
        )

    def test_update_unexistent_status(
            self,
            session: Session,
            statuses_orm: list[Status],
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

    def test_update_without_new_values(self, statuses_orm: list[Status]):
        # Make an attempt to create statement without values.
        status = choice(statuses_orm).status
        with pytest.raises(ValueError) as error:
            self.manager.update(where=dict(status=status), set_value=dict())
        msg = 'Without new values, updating can\'t proceed, set_value={}.'
        assert str(error.value) == msg


@pytest.mark.run(order=1.00_04)
class TestDelete(BaseTestStatus):

    def test_delete_status_with_status_number(
            self,
            session: Session,
            statuses_orm: list[Status],
    ):
        count_before = len(statuses_orm)
        status_to_delete = choice(statuses_orm)

        # The deleted instance must be returned after delete.
        statement = self.manager.delete(status=status_to_delete.status)
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 1
        self.compare_obj_before_after(status_to_delete, instance[0])

        # Ensure that the object is deleted from the DB.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == count_before - 1

        exp = [f's.{f}=={repr(getattr(status_to_delete, f))}' for f in self.fields]
        exp = ' and '.join(exp)  # "s.status==... and s.description=='...' and ..."
        found = list(filter(lambda s: eval(exp), instances))
        assert len(found) == 0

    def test_delete_unexistent_status(
            self,
            session: Session,
            statuses_orm: list[Status],
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
