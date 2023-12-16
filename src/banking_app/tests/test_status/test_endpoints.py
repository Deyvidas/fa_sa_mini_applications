import pytest

from copy import deepcopy
from fastapi import status
from sqlalchemy.orm.session import Session
from typing import Sequence

from src.banking_app.models.status import Status
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.tests.test_status.conftest import BaseTestStatus as BaseTest


@pytest.mark.run(order=2.00_00)
class TestRetrieve(BaseTest):

    def test_get_all_statuses(self, statuses_orm: list[Status]):
        response = self.client.get(f'{self.prefix}/list')
        assert response.status_code == status.HTTP_200_OK

        body = response.json()
        assert body is not None and isinstance(body, list)
        assert len(body) == len(statuses_orm)

    @pytest.mark.parametrize(
        argnames='status_code',
        argvalues=(
            pytest.param(status.HTTP_200_OK, id='existent status number'),
            pytest.param(status.HTTP_404_NOT_FOUND, id='unexistent status number'),
        ),
    )
    def test_get_status_with_number(
            self,
            statuses_orm: list[Status],
            status_code: int,
    ):
        # Test case when user try to get status with unexistent status number.
        if status_code == status.HTTP_404_NOT_FOUND:
            unexist_status = self.get_unexistent_status_num(statuses_orm)
            response = self.client.get(f'{self.prefix}/{unexist_status}')
            assert response.status_code == status_code

            msg = self.not_found_msg.format(Status.__name__, unexist_status)
            assert response.json() == {'detail': msg}
            return

        for status_db in statuses_orm:
            response = self.client.get(f'{self.prefix}/{status_db.status}')
            assert response.status_code == status_code

            body = response.json()
            assert body is not None and isinstance(body, dict)
            assert set(body.keys()) == set(self.fields)
            self.compare_obj_before_after(status_db, body)


@pytest.mark.run(order=2.00_01)
class TestPost(BaseTest):

    def test_add_status(self, session: Session):
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == 0

        # Make POST query.
        new_status = dict(status=1000, description='Test status number 1000.')
        response = self.client.post(f'{self.prefix}', json=new_status)
        assert response.status_code == status.HTTP_201_CREATED

        # Expect than posted status was returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        assert set(body.keys()) == set(self.fields)
        self.compare_obj_before_after(new_status, body)

        # Check if posted status is saved into DB.
        statement = self.manager.filter()
        statuses = session.scalars(statement).unique().all()
        assert len(statuses) == 1
        self.compare_obj_before_after(new_status, statuses[0])

        # Then POST status with already existed status (status must be unique).
        invalid_status = dict(
            status=new_status['status'],
            description='New status description.',
        )
        response = self.client.post(f'{self.prefix}', json=invalid_status)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Check if an appropriate error message was returned.
        msg = self.not_unique_msg.format(Status.__name__, invalid_status['status'])
        assert response.json() == {'detail': msg}

    def test_add_statuses(
            self,
            session: Session,
            statuses_dto: list[StatusRetrieve],
    ):
        url = f'{self.prefix}/list'
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == 0

        # Make POST query.
        statuses_data = [status.model_dump() for status in statuses_dto]
        response = self.client.post(url, json=statuses_data)
        assert response.status_code == status.HTTP_201_CREATED

        # Expect that posted statuses will be returned in the response body.
        body = response.json()
        assert body is not None and isinstance(body, list)
        assert len(body) == len(statuses_data)
        for data in body:
            assert isinstance(data, dict)
            assert (data.keys()) == set(self.fields)
        self.compare_list_before_after(statuses_data, body)

        # Check if the posted statuses are saved in the DB.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == len(statuses_data)
        self.compare_list_before_after(statuses_data, instances)

        # Make deepcopy to compare length after invalid post.
        statuses_before = deepcopy(instances)

        # After trying to POST one already posted status and some new ones, the
        # new statuses were not saved and the existing status was not saved either.
        new_statuses = list()
        for _ in range(4):
            unexist_status_num = self.get_unexistent_status_num(statuses_data)
            new_statuses.append(dict(
                status=unexist_status_num,
                description=f'Test description {unexist_status_num}',
            ))
        existent_status = [statuses_data[-1]]

        response = self.client.post(url, json=new_statuses + existent_status)  # Invalid status placed at the last!
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Check if an appropriate error message was returned.
        msg = self.not_unique_msg.format(Status.__name__, existent_status[0]['status'])
        assert response.json() == {'detail': msg}

        # Check if the state of the DB has not changed.
        statement = self.manager.filter()
        statuses_after = session.scalars(statement).unique().all()
        assert len(statuses_after) == len(statuses_before)
        self.compare_list_before_after(statuses_before, statuses_after)


@pytest.mark.run(order=2.00_02)
class TestUpdate(BaseTest):

    @pytest.mark.parametrize(
        argnames='method',
        argvalues=(
            pytest.param('PUT', id='PUT query'),
            pytest.param('PATCH', id='PATCH query'),
        ),
    )
    def test_full_update_status_with_status_number(
            self,
            method: str,
            session: Session,
            statuses_orm: list[Status],
    ):
        functions = {
            'PUT': self.client.put,
            'PATCH': self.client.patch,
        }
        query_function = functions.get(method)
        if query_function is None:
            assert False, f'Method `{method}` is not provided for this test.'

        to_update = statuses_orm[-1]
        upd_status_num = to_update.status
        url = f'{self.prefix}/{upd_status_num}'
        new_field_values = dict(description=f'New description for {method}.')

        # Make query.
        response = query_function(url, json=new_field_values)
        assert response.status_code == status.HTTP_200_OK

        # Check than updated object is returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        assert set(body.keys()) == set(self.fields)
        assert body['status'] == upd_status_num
        self.compare_obj_before_after(
            new_field_values,
            body,
            exclude=['status'],
        )

        # Check than object is changed in DB.
        statement = self.manager.filter(status=upd_status_num)
        statuses: Sequence[Status] = session.scalars(statement).unique().all()
        assert len(statuses) == 1
        assert statuses[0].status == upd_status_num
        self.compare_obj_before_after(
            new_field_values,
            statuses[0],
            exclude=['status'],
        )

        # Make deepcopy of objects to compare than after, to prevent changing in list after commit.
        statuses_before = deepcopy(statuses_orm)

        # Then I try to update unexistent status.
        unexist_status = self.get_unexistent_status_num(statuses_orm)
        url = f'{self.prefix}/{unexist_status}'
        response = query_function(url, json=new_field_values)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Check than not found message is returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        msg = self.not_found_msg.format(Status.__name__, unexist_status)
        assert body == {'detail': msg}

        # Check than objects in DB not changed.
        statement = self.manager.filter()
        statuses_after = session.scalars(statement).unique().all()
        assert len(statuses_after) == len(statuses_before)
        self.compare_list_before_after(statuses_before, statuses_after)

    def test_partial_update_status_with_empty_body(
            self,
            session: Session,
            statuses_orm: list[Status],
    ):
        statuses_before = deepcopy(statuses_orm)
        to_update = statuses_orm[-1]
        upd_status_num = to_update.status
        url = f'{self.prefix}/{upd_status_num}'

        # Make PATCH query.
        response = self.client.patch(url, json=dict())
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Check than error message is returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        msg = self.empty_patch_body.format(Status.__name__, upd_status_num)
        assert body == {'detail': msg}

        # Check than objects in DB not changed.
        statement = self.manager.filter()
        statuses_after = session.scalars(statement).unique().all()
        assert len(statuses_after) == len(statuses_before)
        self.compare_list_before_after(statuses_before, statuses_after)


@pytest.mark.run(order=2.00_03)
class TestDelete(BaseTest):

    def test_delete_status_with_status_number(
            self,
            session: Session,
            statuses_orm: list[Status],
    ):
        count = len(statuses_orm)
        status_to_delete = statuses_orm[-1]
        del_status_num = status_to_delete.status
        url = f'{self.prefix}/{del_status_num}'

        # Make DELETE query.
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK

        # Expect than deleted status was returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        assert set(body.keys()) == set(self.fields)
        assert body['status'] == del_status_num
        self.compare_obj_before_after(
            status_to_delete,
            body,
            exclude=['status'],
        )

        # Check than status isn't in the DB.
        statement = self.manager.filter()
        statuses = session.scalars(statement).unique().all()
        assert len(statuses) == (count - 1)
        assert status_to_delete not in statuses

        # Then try DELETE not existent status.
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        msg = self.not_found_msg.format(Status.__name__, del_status_num)
        assert response.json() == {'detail': msg}

        # Check that unsuccessful deletion does not change the len and attributes in the database.
        statement = self.manager.filter()
        statuses_after: list[Status] = list(session.scalars(statement).unique().all())
        assert len(statuses_after) == len(statuses)
        self.compare_list_before_after(statuses_after, statuses)
