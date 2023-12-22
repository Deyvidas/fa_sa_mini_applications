import pytest

from random import choice
from random import sample

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import make_transient
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
        model_dto = model_dto.model_copy(update=self.default_values)
        self.compare_obj_before_after(
            model_dto,
            instance,
            exclude=list(self.related_fields),  # Related fields aren't updated in schemas.
        )

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
        self.compare_list_before_after(models_dto, instances)

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
        models_dto = [m.copy(update=self.default_values) for m in models_dto]
        self.compare_list_before_after(
            models_dto,
            instances,
            exclude=list(self.related_fields),  # Related fields aren't updated in schemas.
        )

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
        for pk in self.primary_keys:
            instance_to_get = choice(models_orm)
            statement = self.manager.filter(**{pk: getattr(instance_to_get, pk)})
            instance = session.scalars(statement).unique().all()
            assert len(instance) == 1
            assert isinstance(instance := instance[0], self.model_orm)
            self.compare_obj_before_after(instance_to_get, instance)

    def test_by_unexistent_primary_key(self, session: Session, models_orm):
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
        get_dto_from_orm = self.SingleAdapter.validate_python

        for pk in (pks := self.primary_keys):
            to_update_dto = get_dto_from_orm(choice(models_orm))

            # Prepare data.
            new_model_dto = self.factory.build(factory_use_construct=True)
            assert type(new_model_dto) is self.model_dto
            # Check if the generated dto model has different values from the instance values.
            while to_update_dto == new_model_dto:
                to_update_dto = get_dto_from_orm(choice(models_orm))
            new_model_dto = new_model_dto.model_copy(
                update={f: getattr(to_update_dto, f) for f in pks - {pk}}
            )
            new_data = self.get_orm_data_from_dto(new_model_dto, exclude={pk})

            # Update by pk must change single instance and return it, with updated field.
            statement = self.manager.update(
                where={pk: getattr(to_update_dto, pk)},
                set_value=new_data,
            )
            instance = session.scalars(statement).unique().all()
            session.commit()
            assert len(instance) == 1
            assert isinstance(instance := instance[0], self.model_orm)
            session.refresh(instance)

            # Check that the updated instance has been returned with updated fields.
            new_model_dto = new_model_dto.model_copy(
                update={pk: getattr(to_update_dto, pk)}
            )
            self.compare_obj_before_after(new_model_dto, instance)

            # Ensure that the instance has new values in the DB.
            statement = self.manager.filter(**{pk: getattr(new_model_dto, pk)})
            instance_after = session.scalars(statement).unique().all()
            assert len(instance_after) == 1
            assert isinstance(instance_after := instance_after[0], self.model_orm)
            self.compare_obj_before_after(instance, instance_after)

    def test_single_unexistent_instance(self, session: Session, models_orm):
        models_dto_before = self.ManyAdapter.validate_python(models_orm)

        for pk in self.primary_keys:

            # Prepare data.
            new_model_dto = self.factory.build(factory_use_construct=True)
            new_data = self.get_orm_data_from_dto(new_model_dto)

            # Make an attempt to update the unexistent instance.
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
            self.compare_list_before_after(models_dto_before, instances_after)

    def test_single_without_new_values(self, session: Session, models_orm):
        instance_to_update = choice(models_orm)

        for pk in (pks := self.primary_keys):
            pk_to_update = getattr(instance_to_update, pk)
            with pytest.raises(ValueError) as error:
                self.manager.update(where={pk: pk_to_update}, set_value=dict())
            msg = UPDATE_WITH_EMPTY_BODY_MSG.format(values=dict())
            assert str(error.value) == msg

            if len(pks) > 1:
                session.rollback()


class BaseTestDelete(BaseTestHelper):

    def test_single_instance_by_pk(self, session: Session, models_orm):
        count_before = len(models_orm)

        for pk in (pks := self.primary_keys):
            instance_to_delete = choice(models_orm)

            # The deleted instance must be returned after delete.
            statement = self.manager.delete(**{pk: getattr(instance_to_delete, pk)})
            instance = session.scalars(statement).unique().all()
            session.commit()
            assert len(instance) == 1
            assert isinstance(instance := instance[0], self.model_orm)
            self.compare_obj_before_after(instance_to_delete, instance)

            # Ensure that the instance is deleted from the DB.
            statement = self.manager.filter()
            instances_after = session.scalars(statement).unique().all()
            assert len(instances_after) == (count_before - 1)

            found = list(filter(
                lambda i: getattr(i, pk) == getattr(instance_to_delete, pk),
                instances_after
            ))
            assert len(found) == 0

            # Return deleted instance in the DB if have more than 1 primary key.
            if len(pks) > 1:
                session.reset()
                make_transient(instance_to_delete)
                session.add(instance_to_delete)
                session.commit()

    def test_single_unexistent_instance(self, session: Session, models_orm):

        # Make an attempt to delete the unexistent instance.
        for pk in self.primary_keys:
            unexistent_pk = self.get_unexistent_numeric_value(
                field=pk,
                objects=models_orm,
            )
            statement = self.manager.delete(**{pk: unexistent_pk})
            instance = session.scalar(statement)
            session.commit()
            assert instance is None

            # Ensure that the instances in the DB not been changed.
            statement = self.manager.filter()
            instances_after = session.scalars(statement).unique().all()
            self.compare_list_before_after(models_orm, instances_after)
