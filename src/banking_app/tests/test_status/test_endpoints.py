import pytest

from random import random

from fastapi import status
from fastapi.testclient import TestClient

from src.banking_app.main import banking_app
from src.banking_app.models.status import StatusDesc


client = TestClient(banking_app)


@pytest.mark.usefixtures('create_and_drop_tables')
class TestGET:

    def test_get_all_statuses(self, create_statuses):
        response = client.get('/status/list')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(create_statuses)

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

            status_resp = response.json()
            assert status_resp['status'] == status_db.status
            assert status_resp['description'] == status_db.description
