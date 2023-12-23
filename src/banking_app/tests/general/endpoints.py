import json as _json

from random import choice
from typing import Callable
from fastapi import status
from pydantic import BaseModel, TypeAdapter
from sqlalchemy.orm.session import Session

from src.banking_app.tests.helpers import BaseTestHelper


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


class BaseTestPost(BaseTestHelper):
    model_dto_post: type[BaseModel]

    @property
    def to_json_single(self) -> Callable:
        return TypeAdapter(self.model_dto_post).dump_json

    @property
    def to_json_many(self) -> Callable:
        return TypeAdapter(list[self.model_dto_post]).dump_json

    def test_add_single(self, freezer, session: Session, models_dto):
        exclude = list(self.primary_keys - set(self.default_values))
        new_object = choice(models_dto).model_copy(update=self.default_values)
        new_object = self.refresh_dto_model(session, new_object)

        # Check that the DB is empty.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == 0

        # Make a POST query and expect that the posted object will be returned.
        url = f'{self.prefix}'
        json = self.to_json_single(new_object)
        response = self.client.post(url, json=_json.loads(json))
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
        exclude = list(self.primary_keys - set(self.default_values))
        new_objects = [m.model_copy(update=self.default_values) for m in models_dto]
        new_objects = [self.refresh_dto_model(session, m) for m in new_objects]

        # Check that the DB is empty.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == 0

        # Make a POST query and expect that the posted objects will be returned.
        url = f'{self.prefix}/list'
        json = self.to_json_many(models_dto)
        response = self.client.post(url, json=_json.loads(json))
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body is not None and isinstance(body, list)
        received_models = self.get_dto_from_many(body)
        self.compare_list_before_after(new_objects, received_models, exclude=exclude)

        # Check if posted objects are saved in the DB.
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        self.compare_list_before_after(new_objects, instances, exclude=exclude)
