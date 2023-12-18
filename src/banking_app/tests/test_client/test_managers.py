import pytest

from random import choice

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import select

from typing import Sequence
from sqlalchemy.orm.session import Session

from src.banking_app.models.client import Client
from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.tests.test_client.conftest import BaseTestClient


@pytest.mark.run(order=1.01_00)
class TestCreate(BaseTestClient):

    def test_base(
            self,
            session: Session,
            clients_dto: Sequence[BaseClientModel],
    ):
        client_data = self.get_required_values(choice(clients_dto))

        # Test that create returns the created instance.
        statement = self.manager.create(**client_data)
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)
        self.compare_obj_before_after(client_data, instance)

        # Check that the object has been created in the DB.
        statement = select(self.model_orm)
        instance_after = session.scalars(statement).unique().all()
        assert len(instance_after) == 1
        assert isinstance(instance_after := instance_after[0], self.model_orm)
        self.compare_obj_before_after(instance, instance_after)

    def test_default_assignment(
            self,
            freezer,
            session: Session,
            clients_dto: Sequence[BaseClientModel],
    ):
        client_data = self.get_required_values(choice(clients_dto))
        # Remove all field which have default value in ORM model.
        [client_data.pop(field) for field in self.default_values.keys()]

        # Ensure that creation can proceed without fields with default values.
        statement = self.manager.create(**client_data)
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)
        # Insert default values into the data for comparison.
        client_data.update(self.default_values)
        self.compare_obj_before_after(client_data, instance)

        # Check that the object has been created in the DB.
        statement = select(self.model_orm)
        instance_after = session.scalars(statement).unique().all()
        assert len(instance_after) == 1
        assert isinstance(instance_after := instance_after[0], self.model_orm)
        self.compare_obj_before_after(instance, instance_after)

    def test_not_unique(
            self,
            session: Session,
            clients_dto: Sequence[BaseClientModel]
    ):
        client_data = self.get_required_values(choice(clients_dto))

        # Create instance of status in DB.
        statement = self.manager.create(**client_data)
        instance = session.scalar(statement)
        session.commit()
        assert isinstance(instance, self.model_orm)

        # Try to create another status object with same fields values.
        statement = self.manager.create(**client_data)
        with pytest.raises(IntegrityError) as error:
            session.scalar(statement)
        kwargs = self.manager.parse_integrity_error(error.value)
        assert kwargs == {'client_id': client_data['client_id']}

        # Check that there are no changes in the DB.
        session.rollback()
        statement = select(self.model_orm)
        instance_after = session.scalars(statement).unique().all()
        assert len(instance_after) == 1
        assert isinstance(instance_after := instance_after[0], self.model_orm)
        self.compare_obj_before_after(instance, instance_after)


@pytest.mark.run(order=1.01_01)
class TestBulkCreate(BaseTestClient):

    def test_base(
            self,
            session: Session,
            clients_dto: Sequence[BaseClientModel],
    ):
        list_kwargs = [self.get_required_values(c) for c in clients_dto]

        # Test if bulk_create returns a list of created instances.
        statement = self.manager.bulk_create(list_kwargs)
        instances = session.scalars(statement).unique().all()
        self.compare_list_before_after(clients_dto, instances)

        # Check that objects have been created in the DB.
        statement = select(self.model_orm)
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(instances, instances_after)

    def test_default_assignment(
            self,
            session: Session,
            clients_dto: Sequence[BaseClientModel],
    ):
        list_kwargs = [self.get_required_values(c) for c in clients_dto]
        # Remove all field which have default value in ORM model.
        for field in self.default_values.keys():
            [k.pop(field) for k in list_kwargs]

        # Ensure that creation can proceed without fields with default values.
        statement = self.manager.bulk_create(list_kwargs)
        instances = session.scalars(statement).unique().all()
        [k.update(self.default_values) for k in list_kwargs]
        self.compare_list_before_after(list_kwargs, instances)

    def test_with_some_not_unique(
            self,
            session: Session,
            clients_dto: Sequence[BaseClientModel],
    ):
        half = int(len(clients_dto) / 2)

        # Saving the first part of having clients.
        first_half = [self.get_required_values(c) for c in clients_dto[:half]]
        statement = self.manager.bulk_create(first_half)
        instances = session.scalars(statement).unique().all()
        session.commit()

        # Try to create new clients that are mixed with already existing clients.
        second_half = [self.get_required_values(c) for c in clients_dto[half:]]
        second_half += [first_half[0], first_half[-1]]
        statement = self.manager.bulk_create(second_half)
        with pytest.raises(IntegrityError) as error:
            session.execute(statement)
        kwargs = self.manager.parse_integrity_error(error.value)
        assert kwargs == {'client_id': first_half[0]['client_id']}

        # Check that there are no changes in the DB.
        session.rollback()
        statement = select(self.model_orm)
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(instances, instances_after)


@pytest.mark.run(order=1.01_02)
class TestFilter(BaseTestClient):

    def test_without_arguments(
            self,
            session: Session,
            clients_orm: Sequence[Client],
    ):
        # Check that filtering without parameters returns all objects from the DB.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        self.compare_list_before_after(clients_orm, instances)

    def test_by_client_id(
            self,
            session: Session,
            clients_orm: Sequence[Client]
    ):
        # Filtering by existent client_id.
        existent_client = choice(clients_orm)
        statement = self.manager.filter(client_id=existent_client.client_id)
        instance = session.scalars(statement).unique().all()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], Client)
        self.compare_obj_before_after(existent_client, instance)

        # Filtering by unexistent client_id.
        unexist_client_id = self.get_unexistent_client_id(clients_orm)
        statement = self.manager.filter(client_id=unexist_client_id)
        instance = session.scalar(statement)
        assert instance is None


@pytest.mark.run(order=1.01_03)
class TestUpdate(BaseTestClient):

    def test_update_single_client_with_client_id(
            self,
            session: Session,
            clients_orm: Sequence[Client],
    ):
        ...
