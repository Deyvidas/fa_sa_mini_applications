import pytest

from fastapi import status
from fastapi.testclient import TestClient

from random import random

from sqlalchemy.orm.session import Session

from src.banking_app.main import banking_app
from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import Status


@pytest.mark.usefixtures('create_and_drop_tables')
class BaseTest:
    client = TestClient(banking_app)
    fields_to_retrieve = set(('status', 'description'))
    manager = StatusManager()
    not_found_msg = '{} with status={} not found.'
    not_unique_msg = '{} with field value status={} already exists.'


@pytest.mark.run(order=2.001)
class TestRetrieve(BaseTest):

    def test_get_all_statuses(self, created_statuses: list[Status]):
        response = self.client.get('/status/list')
        assert response.status_code == status.HTTP_200_OK

        body = response.json()
        assert body is not None and isinstance(body, list)
        assert len(body) == len(created_statuses)

    @pytest.mark.parametrize(
        argnames='status_code',
        argvalues=(
            pytest.param(status.HTTP_200_OK, id='existent status number'),
            pytest.param(status.HTTP_404_NOT_FOUND, id='unexistent status number'),  # noqa: E501
        ),
    )
    def test_get_status_with_number(
            self,
            created_statuses: list[Status],
            status_code: int,
    ):
        # Test case when user try to get status with unexistent status number.
        if status_code == status.HTTP_404_NOT_FOUND:
            existent_statuses = [s.status for s in created_statuses]
            unexistent_status = None
            while unexistent_status is None:
                num = int(random() * 100_000)
                if num in existent_statuses:
                    continue
                unexistent_status = num

            response = self.client.get(f'/status/{unexistent_status}')
            assert response.status_code == status_code

            msg = self.not_found_msg.format(Status.__name__, unexistent_status)
            assert response.json() == {'detail': msg}
            return

        for status_db in created_statuses:
            response = self.client.get(f'/status/{status_db.status}')
            assert response.status_code == status_code

            body = response.json()
            assert body is not None and isinstance(body, dict)
            assert set(body.keys()) == self.fields_to_retrieve
            assert body['status'] == status_db.status
            assert body['description'] == status_db.description


@pytest.mark.run(order=2.002)
class TestPost(BaseTest):

    def test_add_status(self, session: Session):
        # Check if table of statuses is empty.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == 0

        # Make POST query.
        new_status = dict(status=1000, description='Test status number 1000.')
        response = self.client.post('/status', json=new_status)
        assert response.status_code == status.HTTP_201_CREATED

        # Expect than posted status was returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        assert set(body.keys()) == self.fields_to_retrieve
        assert body['status'] == new_status['status']
        assert body['description'] == new_status['description']

        # Check if posted status is saved into DB.
        instances: list[Status] = session.scalars(statement).unique().all()
        assert len(instances) == 1
        assert instances[0].status == new_status['status']
        assert instances[0].description == new_status['description']

        # Then try POST status with not unique status (status is unique field).
        invalid_status = dict(
            status=new_status['status'],
            description='New status description.',
        )
        response = self.client.post('/status', json=invalid_status)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        msg = self.not_unique_msg.format(Status.__name__, invalid_status['status'])  # noqa: E501
        assert response.json() == {'detail': msg}


@pytest.mark.run(order=2.003)
class TestUpdate(BaseTest):
    ...


@pytest.mark.run(order=2.004)
class TestDelete(BaseTest):

    def test_delete_status_with_status_number(
            self,
            session: Session,
            created_statuses: list[Status],
    ):
        count = len(created_statuses)
        status_to_delete = created_statuses[-1]
        del_status_num = status_to_delete.status
        url = f'/status/{del_status_num}'

        # Make DELETE query.
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK

        # Expect than deleted status was returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        assert set(body.keys()) == self.fields_to_retrieve
        assert body['status'] == del_status_num
        assert body['description'] == status_to_delete.description

        # Check than status isn't in the DB.
        statement = self.manager.filter()
        instances: list[Status] = session.scalars(statement).unique().all()
        assert len(instances) == (count - 1)
        assert status_to_delete not in instances

        # Then try DELETE not existent status.
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        msg = self.not_found_msg.format(Status.__name__, del_status_num)
        assert response.json() == {'detail': msg}

        # Check than unsuccess deleting does't change len and attributes in DB.
        statement = self.manager.filter()
        instances: list[Status] = session.scalars(statement).unique().all()
        assert len(instances) == len(instances)
        for before, after in zip(instances, instances):
            assert before.status == after.status
            assert before.description == after.description
