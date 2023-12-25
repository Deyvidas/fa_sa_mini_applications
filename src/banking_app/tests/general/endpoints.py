import json as _json

from random import choice
from typing import Callable
from fastapi import status
from pydantic import BaseModel, TypeAdapter

from sqlalchemy.orm.session import make_transient
from sqlalchemy.orm.session import Session

from src.banking_app.tests.helpers import BaseTestHelper


class APIChange:
    model_dto_post: type[BaseModel]

    @property
    def to_json_single(self) -> Callable:
        return TypeAdapter(self.model_dto_post).dump_json

    @property
    def to_json_many(self) -> Callable:
        return TypeAdapter(list[self.model_dto_post]).dump_json


class BaseTestRetrieve(BaseTestHelper):

    def test_get_all(self, models_orm):
        url = f'{self.prefix}/list'

        # Make a GET query that must return all instances.
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body is not None and isinstance(body, list)

        # Ensure that the received models correspond to the current state of
        # the instances in the DB.
        received_models = self.get_dto_from_many(body)
        self.compare_list_before_after(models_orm, received_models)

    def test_get_by_pk(self, models_orm):
        for pk in self.primary_keys:
            for instance in models_orm:
                url = f'{self.prefix}/{getattr(instance, pk)}'

                # Make a GET query that must return single instances.
                response = self.client.get(url)
                assert response.status_code == status.HTTP_200_OK
                body = response.json()
                assert isinstance(body, dict)

                # Ensure that the received model corresponds to the current
                # state of the instance in the DB.
                received_model = self.get_dto_from_single(body)
                self.compare_obj_before_after(instance, received_model)

    def test_get_by_unexistent_pk(self, models_orm):
        for pk in self.primary_keys:
            unexistent_pk = self.get_unexistent_numeric_value(
                field=pk,
                objects=models_orm
            )
            url = f'{self.prefix}/{unexistent_pk}'

            # Make a GET query that that will return a message indicating that
            # it was not found.
            response = self.client.get(url)
            assert response.status_code == status.HTTP_404_NOT_FOUND
            msg = self.not_found_msg(**{pk: unexistent_pk})
            assert response.json() == {'detail': msg}


class BaseTestPost(BaseTestHelper, APIChange):

    def test_add_single(self, freezer, session: Session, models_dto):
        # Check that the DB is empty.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == 0

        # Prepare data.
        exclude = list(self.primary_keys - set(self.default_values))
        new_object = choice(models_dto).model_copy(update=self.default_values)
        new_object = self.refresh_dto_model(session, new_object)

        # Make a POST query and expect that the posted object will be returned.
        url = f'{self.prefix}'
        json = _json.loads(self.to_json_single(new_object))
        response = self.client.post(url, json=json)
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body is not None and isinstance(body, dict)
        received_model = self.get_dto_from_single(body)
        self.compare_obj_before_after(new_object, received_model, exclude=exclude)

        # Check if posted object is saved in the DB.
        statement = self.manager.filter()
        instance = session.scalars(statement).unique().all()
        assert len(instance) == 1
        assert isinstance(instance := instance[0], self.model_orm)
        self.compare_obj_before_after(new_object, instance, exclude=exclude)

    def test_add_many(self, session: Session, models_dto):
        # Check that the DB is empty.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == 0

        # Prepare data.
        exclude = list(self.primary_keys - set(self.default_values))
        models_dto = [m.model_copy(update=self.default_values) for m in models_dto]
        models_dto = [self.refresh_dto_model(session, m) for m in models_dto]

        # Make a POST query and expect that the posted objects will be returned.
        url = f'{self.prefix}/list'
        json = _json.loads(self.to_json_many(models_dto))
        response = self.client.post(url, json=json)
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body is not None and isinstance(body, list)
        received_models = self.get_dto_from_many(body)
        self.compare_list_before_after(models_dto, received_models, exclude=exclude)

        # Check if posted objects are saved in the DB.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        self.compare_list_before_after(models_dto, instances, exclude=exclude)


class BaseTestFullUpdate(BaseTestHelper, APIChange):

    @property
    def update_method(self) -> Callable:
        return self.client.put

    def test_instance_with_pk(self, session: Session, models_orm):
        for pk in self.primary_keys:
            to_update_dto = self.get_dto_from_single(choice(models_orm))
            to_update_pk = getattr(to_update_dto, pk)
            url = f'{self.prefix}/{to_update_pk}'

            # Prepare data.
            new_data = self.factory.build(factory_use_construct=True)
            required = set(self.model_dto_post.model_json_schema()['properties'].keys())
            update = dict()
            for f in set(new_data.model_fields_set) - (required - self.primary_keys):
                update[f] = getattr(to_update_dto, f)
            new_data = new_data.model_copy(update=update)
            new_data = self.refresh_dto_model(session, new_data)

            # Make a PUT query that must returns an updated object.
            json = _json.loads(self.to_json_single(new_data))
            response = self.update_method(url, json=json)
            assert response.status_code == status.HTTP_200_OK
            body = response.json()
            assert body is not None, isinstance(body, dict)
            received_model = self.get_dto_from_single(body)
            self.compare_obj_before_after(new_data, received_model)

            # Check than object is changed in DB.
            statement = self.manager.filter(**{pk: to_update_pk})
            instance = session.scalar(statement)
            assert instance is not None
            self.compare_obj_before_after(new_data, instance)

    def test_unexistent_instance_with_pk(self, session: Session, models_orm):
        models_dto = self.get_dto_from_many(models_orm)

        for pk in self.primary_keys:
            new_data = self.factory.build(factory_use_construct=True)
            unexistent_pk = self.get_unexistent_numeric_value(
                field=pk,
                objects=models_orm,
            )
            url = f'{self.prefix}/{unexistent_pk}'

            # Make a PUT query that must returns an error message.
            json = _json.loads(self.to_json_single(new_data))
            response = self.update_method(url, json=json)
            assert response.status_code == status.HTTP_404_NOT_FOUND
            body = response.json()
            assert body is not None and isinstance(body, dict)
            msg = self.not_found_msg(**{pk: unexistent_pk})
            assert body == {'detail': msg}

            # Check than objects in the DB not changed.
            statement = self.manager.filter()
            instances_after = session.scalars(statement).unique().all()
            assert len(instances_after) == len(models_dto)
            self.compare_list_before_after(models_dto, instances_after)


class BaseTestPartialUpdate(BaseTestFullUpdate):

    @property
    def update_method(self) -> Callable:
        return self.client.patch

    def test_with_empty_body(self, session: Session, models_orm):
        models_dto = self.get_dto_from_many(models_orm)

        for pk in self.primary_keys:
            to_update_dto = choice(models_dto)
            to_update_pk = getattr(to_update_dto, pk)
            url = f'{self.prefix}/{to_update_pk}'

            # Make a PATCH query with empty body, that must returns the error message.
            response = self.update_method(url, json=dict())
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            body = response.json()
            assert body is not None and isinstance(body, dict)
            msg = self.empty_patch_body(**{pk: to_update_pk})
            assert body == {'detail': msg}

            # Check than objects in the DB not changed.
            statement = self.manager.filter()
            instances_after = session.scalars(statement).unique().all()
            assert len(instances_after) == len(models_dto)
            self.compare_list_before_after(models_dto, instances_after)


class BaseTestDelete(BaseTestHelper):

    def test_instance_with_pk(self, session: Session, models_orm):
        count_before = len(models_orm)

        for pk in (pks := self.primary_keys):
            to_delete_instance = choice(models_orm)
            to_delete_pk = getattr(to_delete_instance, pk)
            url = f'{self.prefix}/{to_delete_pk}'

            # Make a DELETE query, that must returns the deleted object.
            response = self.client.delete(url)
            assert response.status_code == status.HTTP_200_OK
            body = response.json()
            assert body is not None and isinstance(body, dict)
            received_model = self.get_dto_from_single(body)
            self.compare_obj_before_after(to_delete_instance, received_model)

            # Check than object is deleted from the DB.
            statement = self.manager.filter()
            instances_after = session.scalars(statement).unique().all()
            assert len(instances_after) == (count_before - 1)

            found = list(filter(
                lambda i: getattr(i, pk) == getattr(to_delete_instance, pk),
                instances_after
            ))
            assert len(found) == 0

            # Return deleted instance in the DB if have more than 1 primary key.
            if len(pks) > 1:
                session.reset()
                make_transient(to_delete_instance)
                session.add(to_delete_instance)
                session.commit()

    def test_unexistent_instance_with_pk(self, session: Session, models_orm):

        for pk in self.primary_keys:
            unexistent_pk = self.get_unexistent_numeric_value(
                field=pk,
                objects=models_orm,
            )
            url = f'{self.prefix}/{unexistent_pk}'

            # Make a DELETE query with unexistent pk, that must returns the error message.
            response = self.client.delete(url)
            assert response.status_code == status.HTTP_404_NOT_FOUND
            body = response.json()
            assert body is not None and isinstance(body, dict)
            msg = self.not_found_msg(**{pk: unexistent_pk})
            assert body == {'detail': msg}

            # Check than objects in the DB not changed.
            statement = self.manager.filter()
            instances_after = session.scalars(statement).unique().all()
            assert len(instances_after) == len(models_orm)
            self.compare_list_before_after(models_orm, instances_after)
