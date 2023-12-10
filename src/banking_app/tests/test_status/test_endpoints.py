import pytest

from fastapi import status
from fastapi.testclient import TestClient

from random import random

from sqlalchemy.orm.session import Session

from src.banking_app.main import banking_app
from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import StatusDesc


client = TestClient(banking_app)
manager = StatusManager()


@pytest.mark.run(order=2.001)
@pytest.mark.usefixtures('create_and_drop_tables')
class TestGET:

    def test_get_all_statuses(self, create_statuses):
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
            create_statuses: list[StatusDesc],
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

            msg = f'{StatusDesc.__name__} with status={unexist_num} not found.'
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
        instances: list[StatusDesc] = session.scalars(statement).unique().all()
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
        msg = f'{StatusDesc.__name__} with field value status={invalid_status['status']} already exists.'  # noqa: E501
        assert response.json() == {'detail': msg}
