import pytest

from copy import deepcopy
from random import choice
from typing import Sequence
from sqlalchemy.orm.session import Session

from src.banking_app.models.client import Client
from src.banking_app.tests.general.managers import BaseTestBulkCreate
from src.banking_app.tests.general.managers import BaseTestCreate
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
