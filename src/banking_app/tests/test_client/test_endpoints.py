import pytest

from sqlalchemy.orm.session import Session

from src.banking_app.schemas import ClientCreate
from src.banking_app.schemas import ClientFullUpdate
from src.banking_app.schemas import ClientPartialUpdate
from src.banking_app.schemas import ClientRetrieve
from src.banking_app.tests.general.endpoints import BaseTestDelete
from src.banking_app.tests.general.endpoints import BaseTestFullUpdate
from src.banking_app.tests.general.endpoints import BaseTestPartialUpdate
from src.banking_app.tests.general.endpoints import BaseTestPost
from src.banking_app.tests.general.endpoints import BaseTestRetrieve
from src.banking_app.tests.test_client.helpers import ClientTestHelper


@pytest.mark.run(order=2.01_00)
class TestRetrieve(ClientTestHelper, BaseTestRetrieve):
    model_dto = ClientRetrieve

    def test_get_all(self, models_orm):
        return super().test_get_all(models_orm)

    def test_get_by_pk(self, models_orm):
        return super().test_get_by_pk(models_orm)

    def test_get_by_unexistent_pk(self, models_orm):
        return super().test_get_by_unexistent_pk(models_orm)


@pytest.mark.run(order=2.01_01)
class TestPost(ClientTestHelper, BaseTestPost):
    model_dto = ClientRetrieve
    model_dto_post = ClientCreate

    def test_add_single(self, freezer, session: Session, models_dto):
        return super().test_add_single(freezer, session, models_dto)

    def test_add_many(self, session: Session, models_dto):
        return super().test_add_many(session, models_dto)


@pytest.mark.run(order=2.01_02)
class TestFullUpdate(ClientTestHelper, BaseTestFullUpdate):
    model_dto = ClientRetrieve
    model_dto_post = ClientFullUpdate

    def test_instance_with_pk(self, session: Session, models_orm):
        return super().test_instance_with_pk(session, models_orm)

    def test_unexistent_instance_with_pk(self, session: Session, models_orm):
        return super().test_unexistent_instance_with_pk(session, models_orm)


@pytest.mark.run(order=2.01_03)
class TestPartialUpdate(TestFullUpdate, BaseTestPartialUpdate):
    model_dto_post = ClientPartialUpdate

    def test_instance_with_pk(self, session: Session, models_orm):
        return super().test_instance_with_pk(session, models_orm)

    def test_unexistent_instance_with_pk(self, session: Session, models_orm):
        return super().test_unexistent_instance_with_pk(session, models_orm)

    def test_with_empty_body(self, session: Session, models_orm):
        return super().test_with_empty_body(session, models_orm)


@pytest.mark.run(order=2.01_04)
class TestDelete(ClientTestHelper, BaseTestDelete):
    model_dto = ClientRetrieve

    def test_instance_with_pk(self, session: Session, models_orm):
        return super().test_instance_with_pk(session, models_orm)

    def test_unexistent_instance_with_pk(self, session: Session, models_orm):
        return super().test_unexistent_instance_with_pk(session, models_orm)
