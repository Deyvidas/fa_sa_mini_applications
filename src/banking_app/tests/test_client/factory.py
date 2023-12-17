from datetime import date
from datetime import timedelta

from polyfactory.decorators import post_generated
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import PostGenerated
from polyfactory.fields import Use

from random import choice
from random import randint

from typing import Any
from typing import Sequence

from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.tests.test_status.factory import factory_statuses_dto


class ClientFactoryHelper:
    AMOUNT = 9
    CLIENT_ID = 0
    CLIENT_ID_STEP = 1

    @classmethod
    def client_id(cls) -> int:
        cls.CLIENT_ID = cls.CLIENT_ID % (cls.CLIENT_ID_STEP * cls.AMOUNT)
        cls.CLIENT_ID += cls.CLIENT_ID_STEP
        return cls.CLIENT_ID

    @classmethod
    def client_status(cls) -> StatusRetrieve:
        return choice(factory_statuses_dto)

    @classmethod
    def birth_date(cls, _, values: dict[str, Any]) -> date:
        days = randint(365 * 3, 365 * 79)
        return values['reg_date'] - timedelta(days=days)


class ClientFactory(ModelFactory):
    __model__ = BaseClientModel
    __check_model__ = True
    client_id = Use(ClientFactoryHelper.client_id)
    client_status = Use(ClientFactoryHelper.client_status)
    birth_date = PostGenerated(ClientFactoryHelper.birth_date)

    @post_generated
    @classmethod
    def status(cls, client_status: StatusRetrieve) -> int:
        return client_status.status


factory_clients_dto: Sequence[BaseClientModel] = ClientFactory().batch(
    ClientFactoryHelper.AMOUNT,
    factory_use_construct=True,
)
assert len(factory_statuses_dto) >= 4, (
    'Ensure that the factory generates at least 4 clients. It\'s required for'
    ' TestBulkCreate::test_with_some_not_unique.'
)
