import pytest

from random import choice
from sqlalchemy.orm.session import Session

from src.banking_app.models.client import Client
from src.banking_app.tests.general.managers import BaseTestBulkCreate
from src.banking_app.tests.general.managers import BaseTestCreate
from src.banking_app.tests.general.managers import BaseTestDelete
from src.banking_app.tests.general.managers import BaseTestFilter
from src.banking_app.tests.general.managers import BaseTestUpdate
from src.banking_app.tests.test_client.conftest import ClientTestHelper
from src.banking_app.utils.kwargs_parser import KwargsParser


@pytest.mark.run(order=1.01_00)
class TestCreate(ClientTestHelper, BaseTestCreate):

    def test_base(self, session: Session, models_dto):
        return super().test_base(session, models_dto)

    def test_default_assignment(self, freezer, session: Session, models_dto):
        return super().test_default_assignment(freezer, session, models_dto)

    def test_not_unique(self, session: Session, models_dto):
        return super().test_not_unique(session, models_dto)

    def test_client_assigned_to_status(self, session: Session, models_dto):
        data = self.get_orm_data_from_dto(choice(models_dto))

        # Create a client and check if this client is in the status.clients list.
        statement = self.manager.create(**data)
        instance = session.scalar(statement)
        assert isinstance(instance, Client)
        session.commit()
        assert instance in instance.client_status.clients


@pytest.mark.run(order=1.01_01)
class TestBulkCreate(ClientTestHelper, BaseTestBulkCreate):

    def test_base(self, session: Session, models_dto):
        return super().test_base(session, models_dto)

    def test_default_assignment(self, session: Session, models_dto):
        return super().test_default_assignment(session, models_dto)

    def test_with_some_not_unique(self, session: Session, models_dto):
        return super().test_with_some_not_unique(session, models_dto)

    def test_clients_assigned_to_status(self, models_orm):
        for instance in models_orm:
            assert instance in instance.client_status.clients


@pytest.mark.run(order=1.01_02)
class TestFilter(ClientTestHelper, BaseTestFilter):

    def test_without_arguments(self, session: Session, models_orm):
        return super().test_without_arguments(session, models_orm)

    def test_by_primary_key(self, session: Session, models_orm):
        return super().test_by_primary_key(session, models_orm)

    def test_by_unexistent_primary_key(self, session: Session, models_orm):
        return super().test_by_unexistent_primary_key(session, models_orm)

    @pytest.mark.parametrize(
        argnames='attr',
        argvalues=(
            pytest.param('status', id='status'),
            pytest.param('phone', id='phone'),
            pytest.param('VIP_flag', id='VIP_flag'),
            pytest.param('sex', id='sex'),
        ),
    )
    def test_by_single_attribute(self, attr, session: Session, models_orm):
        random_model = choice(models_orm)
        attr_value = getattr(random_model, attr)

        statement = self.manager.filter(**{attr: attr_value})
        instances = session.scalars(statement).unique().all()
        assert len(instances) > 0

        found = list(filter(
            lambda m: getattr(m, attr) == attr_value, models_orm
        ))
        self.compare_list_before_after(found, instances)

    def test_by_multiple_attributes(self, session: Session, models_orm):
        random_model = choice(models_orm)

        dto_model = self.get_dto_from_single(random_model)
        can_filter_by = {'status', 'phone', 'VIP_flag', 'sex'}
        kwargs = dto_model.model_dump(include=can_filter_by)

        statement = self.manager.filter(**kwargs)
        instances = session.scalars(statement).unique().all()
        assert len(instances) > 0

        filter_kwargs = {k: KwargsParser()._value_dump(v) for k, v in kwargs.items()}
        expression = ' and '.join(f'm.{k} == {repr(v)}' for k, v in filter_kwargs.items())
        found = list(filter(lambda m: eval(expression), models_orm))
        self.compare_list_before_after(instances, found)


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
