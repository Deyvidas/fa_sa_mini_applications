import pytest

from copy import deepcopy
from random import choice
from pydantic import TypeAdapter

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import select

from typing import Sequence
from sqlalchemy.orm.session import Session

from src.banking_app.models.client import Client
from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.tests.general.managers import BaseTestCreate
from src.banking_app.tests.test_client.conftest import ClientTestHelper
from src.banking_app.tests.test_client.factory import ClientFactory


@pytest.mark.run(order=1.01_00)
class TestCreate(ClientTestHelper, BaseTestCreate):
    ...


@pytest.mark.run(order=1.01_01)
class TestBulkCreate(ClientTestHelper):

    def test_base(
            self,
            session: Session,
            clients_dto: Sequence[BaseClientModel],
    ):
        list_kwargs = [self.get_orm_data_from_dto(c) for c in clients_dto]

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
        list_kwargs = [self.get_orm_data_from_dto(c) for c in clients_dto]
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
        first_half = [self.get_orm_data_from_dto(c) for c in clients_dto[:half]]
        statement = self.manager.bulk_create(first_half)
        instances = session.scalars(statement).unique().all()
        session.commit()

        # Try to create new clients that are mixed with already existing clients.
        second_half = [self.get_orm_data_from_dto(c) for c in clients_dto[half:]]
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
class TestFilter(ClientTestHelper):

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
class TestUpdate(ClientTestHelper):
    AdapterOne = TypeAdapter(ClientTestHelper.model_dto).validate_python

    def test_update_single_client_with_client_id(
            self,
            session: Session,
            clients_orm: Sequence[Client],
    ):
        client_to_update = choice(clients_orm)

        # Prepare data.
        new_client_dto = ClientFactory().build(factory_use_construct=True)
        while self.AdapterOne(client_to_update) == new_client_dto:
            client_to_update = choice(clients_orm)
        client_to_update = deepcopy(client_to_update)  # To save original state.
        new_data = self.get_orm_data_from_dto(new_client_dto, exclude={'client_id'})

        # Update must change single client and return it with updated field values.
        statement = self.manager.update(
            where=dict(client_id=client_to_update.client_id),
            set_value=new_data,
        )
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)

        # Check that the updated client has been returned with updated fields.
        new_data['client_id'] = client_to_update.client_id
        self.compare_obj_before_after(new_data, instance)

        # Ensure that the object has new values in the DB.
        statement = self.manager.filter(client_id=instance.client_id)
        instance_after = session.scalars(statement).unique().all()
        assert len(instance_after) == 1
        assert isinstance(instance_after := instance_after[0], self.model_orm)
        self.compare_obj_before_after(instance, instance_after)

    def test_update_unexistent_client(
            self,
            session: Session,
            clients_orm: Sequence[Client],
    ):
        instances_before = deepcopy(clients_orm)

        # Prepare new data.
        new_data = ClientFactory.build(factory_use_construct=True)
        new_data = self.get_orm_data_from_dto(new_data, exclude={'client_id'})

        # Make an attempt to update the client with an unexistent client_id.
        unexist_client_id = self.get_unexistent_client_id(clients_orm)
        statement = self.manager.update(
            where=dict(client_id=unexist_client_id),
            set_value=new_data,
        )
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 0

        # Ensure that the objects in the DB not been changed.
        statement = self.manager.filter()
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(instances_before, instances_after)

    def test_update_without_new_values(self, clients_orm: Sequence[Client]):
        # Make an attempt to create statement without values.
        client_id = choice(clients_orm).client_id
        with pytest.raises(ValueError) as error:
            self.manager.update(where=dict(client_id=client_id), set_value=dict())
        msg = 'Without new values, updating can\'t proceed, set_value={}.'
        assert str(error.value) == msg


@pytest.mark.run(order=1.01_04)
class TestDelete(ClientTestHelper):

    def test_delete_client_with_client_id(
            self,
            session: Session,
            clients_orm: Sequence[Client],
    ):
        count_before = len(clients_orm)
        client_to_delete = choice(clients_orm)

        # The deleted instance must be returned after delete.
        statement = self.manager.delete(client_id=client_to_delete.client_id)
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)
        self.compare_obj_before_after(client_to_delete, instance)

        # Ensure that the object is deleted from the DB.
        statement = self.manager.filter()
        instances: Sequence[Client] = session.scalars(statement).unique().all()
        assert len(instances) == count_before - 1

        found = list(filter(
            lambda i: i.client_id == client_to_delete.client_id, instances
        ))
        assert len(found) == 0

    def test_delete_unexistent_client(
            self,
            session: Session,
            clients_orm: Sequence[Client],
    ):
        clients_before = deepcopy(clients_orm)

        # Make an attempt to delete the client with an unexistent client_id.
        unexist_client_id = self.get_unexistent_client_id(clients_orm)
        statement = self.manager.delete(client_id=unexist_client_id)
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 0

        # Ensure that the objects in the DB not been changed.
        statement = self.manager.filter()
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(clients_before, instances_after)
