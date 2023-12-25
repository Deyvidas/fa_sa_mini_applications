import json as _json
import pytest

from fastapi import status as _status

from random import choice
from random import sample

from sqlalchemy.orm.session import Session

from src.banking_app.schemas import StatusCreate
from src.banking_app.schemas import StatusFullUpdate
from src.banking_app.schemas import StatusPartialUpdate
from src.banking_app.schemas import StatusRetrieve
from src.banking_app.tests.general.endpoints import BaseTestDelete
from src.banking_app.tests.general.endpoints import BaseTestFullUpdate
from src.banking_app.tests.general.endpoints import BaseTestPartialUpdate
from src.banking_app.tests.general.endpoints import BaseTestPost
from src.banking_app.tests.general.endpoints import BaseTestRetrieve
from src.banking_app.tests.test_status.helpers import StatusTestHelper


@pytest.mark.run(order=2.00_00)
class TestRetrieve(StatusTestHelper, BaseTestRetrieve):
    model_dto = StatusRetrieve

    def test_get_all(self, models_orm):
        return super().test_get_all(models_orm)

    def test_get_by_pk(self, models_orm):
        return super().test_get_by_pk(models_orm)

    def test_get_by_unexistent_pk(self, models_orm):
        return super().test_get_by_unexistent_pk(models_orm)


@pytest.mark.run(order=2.00_01)
class TestPost(StatusTestHelper, BaseTestPost):
    model_dto = StatusRetrieve
    model_dto_post = StatusCreate

    def test_add_single(self, freezer, session: Session, models_dto):
        return super().test_add_single(freezer, session, models_dto)

    def test_add_many(self, session: Session, models_dto):
        return super().test_add_many(session, models_dto)

    def test_add_not_unique_status(self, session: Session, models_orm):
        url = f'{self.prefix}'
        json = _json.loads(self.to_json_single(choice(models_orm)))
        response = self.client.post(url, json=json)
        assert response.status_code == _status.HTTP_400_BAD_REQUEST
        # Check if an appropriate error message was returned.
        kwargs = {pk: json[pk] for pk in self.primary_keys}
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
        json = _json.loads(self.to_json_many(second_half))
        response = self.client.post(url, json=json)
        assert response.status_code == _status.HTTP_400_BAD_REQUEST
        # Check if an appropriate error message was returned.
        kwargs = {pk: getattr(existent[0], pk) for pk in self.primary_keys}
        assert response.json() == {'detail': self.not_unique_msg(**kwargs)}

        # Check if the state of the DB has not changed.
        statement = self.manager.filter()
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(instances_f_h, instances_after)


@pytest.mark.run(order=2.00_02)
class TestFullUpdate(StatusTestHelper, BaseTestFullUpdate):
    model_dto = StatusRetrieve
    model_dto_post = StatusFullUpdate

    def test_instance_with_pk(self, session: Session, models_orm):
        return super().test_instance_with_pk(session, models_orm)

    def test_unexistent_instance_with_pk(self, session: Session, models_orm):
        return super().test_unexistent_instance_with_pk(session, models_orm)


@pytest.mark.run(order=2.00_03)
class TestPartialUpdate(TestFullUpdate, BaseTestPartialUpdate):
    model_dto_post = StatusPartialUpdate

    def test_instance_with_pk(self, session: Session, models_orm):
        return super().test_instance_with_pk(session, models_orm)

    def test_unexistent_instance_with_pk(self, session: Session, models_orm):
        return super().test_unexistent_instance_with_pk(session, models_orm)

    def test_with_empty_body(self, session: Session, models_orm):
        return super().test_with_empty_body(session, models_orm)


@pytest.mark.run(order=2.00_04)
class TestDelete(StatusTestHelper, BaseTestDelete):
    model_dto = StatusRetrieve

    def test_instance_with_pk(self, session: Session, models_orm):
        return super().test_instance_with_pk(session, models_orm)

    def test_unexistent_instance_with_pk(self, session: Session, models_orm):
        return super().test_unexistent_instance_with_pk(session, models_orm)
