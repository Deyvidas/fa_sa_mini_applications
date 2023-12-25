import pytest

from sqlalchemy.orm.session import Session

from src.banking_app.tests.general.managers import BaseTestBulkCreate
from src.banking_app.tests.general.managers import BaseTestCreate
from src.banking_app.tests.general.managers import BaseTestDelete
from src.banking_app.tests.general.managers import BaseTestFilter
from src.banking_app.tests.general.managers import BaseTestUpdate
from src.banking_app.tests.test_client.conftest import ClientTestHelper


@pytest.mark.run(order=1.01_00)
class TestCreate(ClientTestHelper, BaseTestCreate):

    def test_base(self, session: Session, models_dto):
        return super().test_base(session, models_dto)

    def test_default_assignment(self, freezer, session: Session, models_dto):
        return super().test_default_assignment(freezer, session, models_dto)

    def test_not_unique(self, session: Session, models_dto):
        return super().test_not_unique(session, models_dto)


@pytest.mark.run(order=1.01_01)
class TestBulkCreate(ClientTestHelper, BaseTestBulkCreate):

    def test_base(self, session: Session, models_dto):
        return super().test_base(session, models_dto)

    def test_default_assignment(self, session: Session, models_dto):
        return super().test_default_assignment(session, models_dto)

    def test_with_some_not_unique(self, session: Session, models_dto):
        return super().test_with_some_not_unique(session, models_dto)


@pytest.mark.run(order=1.01_02)
class TestFilter(ClientTestHelper, BaseTestFilter):

    def test_without_arguments(self, session: Session, models_orm):
        return super().test_without_arguments(session, models_orm)

    def test_by_primary_key(self, session: Session, models_orm):
        return super().test_by_primary_key(session, models_orm)

    def test_by_unexistent_primary_key(self, session: Session, models_orm):
        return super().test_by_unexistent_primary_key(session, models_orm)


@pytest.mark.run(order=1.01_03)
class TestUpdate(ClientTestHelper, BaseTestUpdate):

    def test_single_instance_by_pk(self, session: Session, models_orm):
        return super().test_single_instance_by_pk(session, models_orm)

    def test_single_unexistent_instance(self, session: Session, models_orm):
        return super().test_single_unexistent_instance(session, models_orm)

    def test_single_without_new_values(self, session: Session, models_orm):
        return super().test_single_without_new_values(session, models_orm)


@pytest.mark.run(order=1.01_04)
class TestDelete(ClientTestHelper, BaseTestDelete):

    def test_single_instance_by_pk(self, session: Session, models_orm):
        return super().test_single_instance_by_pk(session, models_orm)

    def test_single_unexistent_instance(self, session: Session, models_orm):
        return super().test_single_unexistent_instance(session, models_orm)
