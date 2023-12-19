import pytest

from copy import deepcopy
from pydantic import TypeAdapter

from random import choice
from random import sample

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select

from src.banking_app.tests.helpers import BaseTestHelper
from src.banking_app.managers.base import UPDATE_WITH_EMPTY_BODY_MSG


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


class BaseTestBulkCreate(BaseTestHelper):

    def test_base(self, session: Session, models_dto):
        list_kwargs = [self.get_orm_data_from_dto(m) for m in models_dto]

        # Test if bulk_create returns a list of created instances.
        statement = self.manager.bulk_create(list_kwargs)
        instances = session.scalars(statement).unique().all()
        session.commit()
        self.compare_list_before_after(list_kwargs, instances)

        # Check that objects have been created in the DB.
        statement = select(self.model_orm)
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(instances, instances_after)

    def test_with_some_not_unique(self, session: Session, models_dto):
        half = int(len(models_dto) / 2)

        # Saving the first part of having models.
        first_half = [self.get_orm_data_from_dto(m) for m in models_dto[:half]]
        statement = self.manager.bulk_create(first_half)
        instances_f_h = session.scalars(statement).unique().all()
        session.commit()

        # Try to create new instances that are mixed with already existing instances.
        second_half = [self.get_orm_data_from_dto(m) for m in models_dto[half:]]
        second_half += (existent := sample(first_half, 2))
        statement = self.manager.bulk_create(second_half)
        with pytest.raises(IntegrityError) as error:
            session.scalars(statement).unique().all()
        kwargs = self.manager.parse_integrity_error(error.value)
        # IntegrityError raised for first not unique.
        assert kwargs == {pk: existent[0][pk] for pk in self.primary_keys}

        # Check that there are no changes in the DB.
        session.rollback()
        statement = select(self.model_orm)
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(instances_f_h, instances_after)

    def test_default_assignment(self, session: Session, models_dto):
        exclude = set(self.default_values.keys())
        list_kwargs = [self.get_orm_data_from_dto(m, exclude=exclude) for m in models_dto]

        # Ensure that creation can proceed without fields with default values.
        statement = self.manager.bulk_create(list_kwargs)
        instances = session.scalars(statement).unique().all()
        session.commit()

        # Insert default values into the data for comparison.
        [k.update(self.default_values) for k in list_kwargs]
        self.compare_list_before_after(list_kwargs, instances)

        # Check that the object has been created in the DB.
        statement = select(self.model_orm)
        instances_after = session.scalars(statement).unique().all()
        self.compare_list_before_after(instances, instances_after)


class BaseTestFilter(BaseTestHelper):

    def test_without_arguments(self, session: Session, models_orm):
        # Check that filtering without parameters returns all objects from the DB.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        self.compare_list_before_after(models_orm, instances)

    def test_by_primary_key(self, session: Session, models_orm):
        # Filtering by existent primary keys.
        existent_instance = choice(models_orm)
        for pk in self.primary_keys:
            statement = self.manager.filter(**{pk: getattr(existent_instance, pk)})
            instance = session.scalars(statement).unique().all()
            assert len(instance) == 1
            assert isinstance(instance := instance[0], self.model_orm)
            self.compare_obj_before_after(existent_instance, instance)

        # Filtering by unexistent primary keys.
        for pk in self.primary_keys:
            unexistent_pk = self.get_unexistent_numeric_value(
                field=pk,
                objects=models_orm,
            )
            statement = self.manager.filter(**{pk: unexistent_pk})
            instance = session.scalar(statement)
            assert instance is None


class BaseTestUpdate(BaseTestHelper):

    def test_single_instance_by_pk(self, session: Session, models_orm):
        get_dto_from_orm = TypeAdapter(self.model_dto).validate_python

        for pk in (pks := self.primary_keys):
            instance_to_update = choice(models_orm)

            # Prepare data.
            new_model_dto = self.factory.build(factory_use_construct=True)
            assert type(new_model_dto) is self.model_dto
            # Check if the generated dto model has different values from the instance values.
            while get_dto_from_orm(instance_to_update) == new_model_dto:
                instance_to_update = choice(models_orm)
            instance_to_update = deepcopy(instance_to_update)  # To save original state.
            # Exclude current pk and for other primary keys set value equal to instance_to_update.
            new_data = self.get_orm_data_from_dto(new_model_dto, exclude={pk})
            [new_data.update({f: getattr(instance_to_update, f)}) for f in pks - {pk}]

            # Update by pk must change single instance and return it, with updated field.
            statement = self.manager.update(
                where={pk: getattr(instance_to_update, pk)},
                set_value=new_data,
            )
            instance = session.scalars(statement).unique().all()
            session.commit()
            assert len(instance) == 1
            assert isinstance(instance := instance[0], self.model_orm)

            # Check that the updated instance has been returned with updated fields.
            new_data.update({pk: getattr(instance_to_update, pk)})
            self.compare_obj_before_after(instance, new_data)

            # Ensure that the instance has new values in the DB.
            statement = self.manager.filter(**{pk: getattr(instance_to_update, pk)})
            instance_after = session.scalars(statement).unique().all()
            assert len(instance_after) == 1
            assert isinstance(instance_after := instance_after[0], self.model_orm)
            self.compare_obj_before_after(instance, instance_after)

    def test_single_unexistent_instance(self, session: Session, models_orm):
        instances_before = deepcopy(models_orm)

        for pk in self.primary_keys:

            # Prepare data.
            new_model_dto = self.factory.build(factory_use_construct=True)
            new_data = self.get_orm_data_from_dto(new_model_dto)

            # Make an attempt to update the instance with an unexistent pk.
            unexistent_pk = self.get_unexistent_numeric_value(
                field=pk,
                objects=models_orm,
            )
            statement = self.manager.update(
                where={pk: unexistent_pk},
                set_value=new_data,
            )
            instance = session.scalar(statement)
            session.commit()
            assert instance is None

            # Ensure that the objects in the DB not been changed.
            statement = self.manager.filter()
            instances_after = session.scalars(statement).unique().all()
            self.compare_list_before_after(instances_before, instances_after)

    def test_single_without_new_values(self, session: Session, models_orm):
        instance_to_update = choice(models_orm)

        for pk in self.primary_keys:
            pk_to_update = getattr(instance_to_update, pk)
            with pytest.raises(ValueError) as error:
                self.manager.update(where={pk: pk_to_update}, set_value=dict())
            msg = UPDATE_WITH_EMPTY_BODY_MSG.format(values=dict())
            assert str(error.value) == msg
            session.rollback()
