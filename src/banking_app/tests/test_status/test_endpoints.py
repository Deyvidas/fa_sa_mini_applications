import pytest

from fastapi import status
from fastapi.testclient import TestClient

from random import random

from typing import NewType

from sqlalchemy.orm.session import Session

from src.banking_app.main import banking_app
from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import StatusDesc


client = TestClient(banking_app)
manager = StatusManager()


LS = NewType('LS', list[StatusDesc])
S = NewType('S', StatusDesc)


@pytest.mark.run(order=2.001)
@pytest.mark.usefixtures('create_and_drop_tables')
class TestGET:
    not_unique_msg = '{} with field value status={} already exists.'
    not_found_msg = '{} with status={} not found.'

    def test_get_all_statuses(self, create_statuses: LS):
        response = client.get('/status/list')
        assert response.status_code == status.HTTP_200_OK

        body = response.json()
        assert body is not None and isinstance(body, list)
        assert len(body) == len(create_statuses)

    @pytest.mark.parametrize(
        argnames='status_code',
        argvalues=(
            pytest.param(status.HTTP_200_OK, id='existent status number'),
            pytest.param(status.HTTP_404_NOT_FOUND, id='unexistent status number'),  # noqa: E501
        ),
    )
    def test_get_status_with_number(
            self,
            create_statuses: LS,
            status_code: int,
    ):
        # Test case when user try to get status with unexistent status number.
        if status_code == status.HTTP_404_NOT_FOUND:
            existent_nums = [s.status for s in create_statuses]
            unexist_num = None
            while unexist_num is None:
                num = int(random() * 100_000)
                if num in existent_nums:
                    continue
                unexist_num = num

            response = client.get(f'/status/{unexist_num}')
            assert response.status_code == status_code

            msg = self.not_found_msg.format(StatusDesc.__name__, unexist_num)
            assert response.json() == {'detail': msg}
            return

        for status_db in create_statuses:
            response = client.get(f'/status/{status_db.status}')
            assert response.status_code == status_code

            body = response.json()
            assert body is not None and isinstance(body, dict)
            assert body['status'] == status_db.status
            assert body['description'] == status_db.description

    def test_add_status(self, session: Session):
        # Check if table of statuses is empty.
        statement = manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == 0

        new_status = dict(status=1000, description='Test status number 1000.')
        response = client.post('/status', json=new_status)
        assert response.status_code == status.HTTP_201_CREATED

        # Expect than posted status was returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        assert body['status'] == new_status['status']
        assert body['description'] == new_status['description']

        # Check if posted status is saved into DB.
        instances: LS = session.scalars(statement).unique().all()
        assert len(instances) == 1
        assert instances[0].status == new_status['status']
        assert instances[0].description == new_status['description']

        # Then try POST status with not unique status (status is unique field).
        invalid_status = dict(
            status=new_status['status'],
            description='New status description.',
        )
        response = client.post('/status', json=invalid_status)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        msg = self.not_unique_msg.format(StatusDesc.__name__, invalid_status['status'])  # noqa: E501
        assert response.json() == {'detail': msg}

    def test_delete_status_with_status_number(
            self,
            session: Session,
            create_statuses: LS,
    ):
        if (count := len(create_statuses)) == 0:
            assert False, f'Created statuses={count} required min 1.'
        status_to_delete = create_statuses[-1]
        url = f'/status/{status_to_delete.status}'

        response = client.delete(url)
        assert response.status_code == status.HTTP_200_OK

        # Expect than deleted status was returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        assert body['status'] == status_to_delete.status
        assert body['description'] == status_to_delete.description

        # Check than status isn't in the DB.
        instances: LS = session.scalars(manager.filter()).unique().all()
        assert len(instances) == (count - 1)
        assert status_to_delete not in instances

        # Then try DELETE not existent status.
        response = client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        msg = self.not_found_msg.format(StatusDesc.__name__, status_to_delete.status)  # noqa: E501
        assert response.json() == {'detail': msg}

        # Check than unsuccess deleting does't change len&attributes in DB.
        instances_after: LS = session.scalars(manager.filter()).unique().all()
        assert len(instances) == len(instances_after)
        for before, after in zip(instances, instances_after):
            assert before.status == after.status
            assert before.description == after.description
