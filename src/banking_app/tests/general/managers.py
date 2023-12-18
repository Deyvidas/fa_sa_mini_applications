import pytest

from random import choice

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select

from src.banking_app.tests.helpers import BaseTestHelper


class BaseTestCreate(BaseTestHelper):

    def test_base(self, session: Session, models_dto):
        model_dto = choice(models_dto)

        # Test that create returns the created instance.
        statement = self.manager.create(**self.get_orm_data_from_dto(model_dto))
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)
        self.compare_obj_before_after(model_dto, instance)

        # Check that the object has been created in the DB.
        statement = select(self.model_orm)
        instance_after = session.scalars(statement).unique().all()
        assert len(instance_after) == 1
        assert isinstance(instance_after := instance_after[0], self.model_orm)
        self.compare_obj_before_after(instance, instance_after)

    def test_not_unique(self, session: Session, models_dto):
        model_dto = choice(models_dto)

        # Create instance in DB.
        statement = self.manager.create(**self.get_orm_data_from_dto(model_dto))
        instance = session.scalar(statement)
        session.commit()
        assert isinstance(instance, self.model_orm)

        # Try to create another status object with same fields values.
        statement = self.manager.create(**self.get_orm_data_from_dto(model_dto))
        with pytest.raises(IntegrityError) as error:
            session.scalar(statement)
        kwargs = self.manager.parse_integrity_error(error.value)
        assert kwargs == {pk: getattr(model_dto, pk) for pk in self.primary_keys}

        # Check that there are no changes in the DB.
        session.rollback()
        statement = select(self.model_orm)
        instance_after = session.scalars(statement).unique().all()
        assert len(instance_after) == 1
        assert isinstance(instance_after := instance_after[0], self.model_orm)
        self.compare_obj_before_after(instance, instance_after)

    def test_default_assignment(self, freezer, session: Session, models_dto):
        model_dto = choice(models_dto)
        exclude = set(self.default_values.keys())
        data = self.get_orm_data_from_dto(model_dto, exclude=exclude)

        # Ensure that creation can proceed without fields with default values.
        statement = self.manager.create(**data)
        instance = session.scalars(statement).unique().all()
        session.commit()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)

        # Insert default values into the data for comparison.
        data.update(self.default_values)
        self.compare_obj_before_after(instance, data)

        # Check that the object has been created in the DB.
        statement = select(self.model_orm)
        instance_after = session.scalars(statement).unique().all()
        assert len(instance_after) == 1
        assert isinstance(instance_after := instance_after[0], self.model_orm)
        self.compare_obj_before_after(instance, instance_after)
