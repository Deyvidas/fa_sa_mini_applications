import json as _json
import pytest

from copy import deepcopy
from fastapi import status as _status
from random import choice, sample
from sqlalchemy.orm.session import Session
from typing import Sequence

from src.banking_app.models.status import Status
from src.banking_app.schemas import StatusCreate
from src.banking_app.schemas import StatusRetrieve
from src.banking_app.tests.general.endpoints import BaseTestPost
from src.banking_app.tests.general.endpoints import BaseTestRetrieve
from src.banking_app.tests.test_status.helpers import StatusTestHelper


@pytest.mark.run(order=2.00_00)
class TestRetrieve(StatusTestHelper, BaseTestRetrieve):
    model_dto = StatusRetrieve


@pytest.mark.run(order=2.00_01)
class TestPost(StatusTestHelper, BaseTestPost):
    model_dto = StatusRetrieve
    model_dto_post = StatusCreate

    def test_add_not_unique_status(self, session: Session, models_orm):
        url = f'{self.prefix}'
        json = self.to_json_single(choice(models_orm))
        response = self.client.post(url, json=_json.loads(json))
        assert response.status_code == _status.HTTP_400_BAD_REQUEST
        # Check if an appropriate error message was returned.
        kwargs = {pk: _json.loads(json)[pk] for pk in self.primary_keys}
        assert response.json() == {'detail': self.not_unique_msg(**kwargs)}

    def test_add_some_not_unique_statuses(self, session: Session, models_dto):
        url = f'{self.prefix}/list'
        half = int(len(models_dto) / 2)

        # Add first half in the DB.
        first_half = models_dto[:half]
        list_kwargs = [self.get_orm_data_from_dto(m) for m in first_half]
        statement = self.manager.bulk_create(list_kwargs)
        instances_f_h = session.scalars(statement).unique().all()
        session.commit()

        # Try to POST new objects along with the ones already existing in the DB.
        second_half = models_dto[half:]
        second_half += (existent := sample(first_half, 2))
        json = self.to_json_many(second_half)
        response = self.client.post(url, json=_json.loads(json))
        assert response.status_code == _status.HTTP_400_BAD_REQUEST
        # Check if an appropriate error message was returned.
        kwargs = {pk: getattr(existent[0], pk) for pk in self.primary_keys}
        assert response.json() == {'detail': self.not_unique_msg(**kwargs)}

        # Check if the state of the DB has not changed.
        statement = self.manager.filter()
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(instances_f_h, instances_after)


@pytest.mark.run(order=2.00_02)
class TestUpdate(StatusTestHelper):

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
            statuses_orm: Sequence[Status],
    ):
        functions = {
            'PUT': self.client.put,
            'PATCH': self.client.patch,
        }
        query_function = functions.get(method)
        if query_function is None:
            assert False, f'Method `{method}` is not provided for this test.'

        to_update = choice(statuses_orm)
        upd_status_num = to_update.status
        url = f'{self.prefix}/{upd_status_num}'
        new_field_values = dict(description=f'New description for {method}.')

        # Make query.
        response = query_function(url, json=new_field_values)
        assert response.status_code == _status.HTTP_200_OK

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
        instance = session.scalars(statement).unique().all()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)
        assert instance.status == upd_status_num
        self.compare_obj_before_after(
            new_field_values,
            instance,
            exclude=['status'],
        )

        # Make deepcopy of objects to compare than after, to prevent changing in list after commit.
        instances_before = deepcopy(statuses_orm)

        # Then I try to update unexistent status.
        unexist_status = self.get_unexistent_status_num(statuses_orm)
        url = f'{self.prefix}/{unexist_status}'
        response = query_function(url, json=new_field_values)
        assert response.status_code == _status.HTTP_404_NOT_FOUND

        # Check than not found message is returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        msg = self.not_found_msg(status=unexist_status)
        assert body == {'detail': msg}

        # Check than objects in DB not changed.
        statement = self.manager.filter()
        instances_after = session.scalars(statement).unique().all()
        assert len(instances_after) == len(instances_before)
        self.compare_list_before_after(instances_before, instances_after)

    def test_partial_update_status_with_empty_body(
            self,
            session: Session,
            statuses_orm: Sequence[Status],
    ):
        instances_before = deepcopy(statuses_orm)
        to_update = choice(statuses_orm)
        upd_status_num = to_update.status
        url = f'{self.prefix}/{upd_status_num}'

        # Make PATCH query.
        response = self.client.patch(url, json=dict())
        assert response.status_code == _status.HTTP_400_BAD_REQUEST

        # Check than error message is returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        msg = self.empty_patch_body(status=upd_status_num)
        assert body == {'detail': msg}

        # Check than objects in DB not changed.
        statement = self.manager.filter()
        instances_after = session.scalars(statement).unique().all()
        assert len(instances_after) == len(instances_before)
        self.compare_list_before_after(instances_before, instances_after)


@pytest.mark.run(order=2.00_03)
class TestDelete(StatusTestHelper):

    def test_delete_status_with_status_number(
            self,
            session: Session,
            statuses_orm: Sequence[Status],
    ):
        count = len(statuses_orm)
        status_to_delete = choice(statuses_orm)
        del_status_num = status_to_delete.status
        url = f'{self.prefix}/{del_status_num}'

        # Make DELETE query.
        response = self.client.delete(url)
        assert response.status_code == _status.HTTP_200_OK

        # Expect than deleted status was returned.
        body = response.json()
        assert body is not None and isinstance(body, dict)
        assert set(body.keys()) == set(self.fields)
        self.compare_obj_before_after(status_to_delete, body)

        # Check than status isn't in the DB.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == (count - 1)
        exp = [f's.{f}=={repr(getattr(status_to_delete, f))}' for f in self.fields]
        exp = ' and '.join(exp)
        found = list(filter(lambda s: eval(exp), instances))
        assert len(found) == 0

        # Then try DELETE not existent status.
        response = self.client.delete(url)
        assert response.status_code == _status.HTTP_404_NOT_FOUND
        msg = self.not_found_msg(status=del_status_num)
        assert response.json() == {'detail': msg}

        # Check that unsuccessful deletion does not change the len and attributes in the database.
        statement = self.manager.filter()
        instances_after: Sequence[Status] = list(session.scalars(statement).unique().all())
        assert len(instances_after) == len(instances)
        self.compare_list_before_after(instances_after, instances)
