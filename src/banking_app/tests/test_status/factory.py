from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use

from typing import Sequence

from src.banking_app.schemas import StatusModelWithRelations
from src.banking_app.models.client import DEFAULT_CLIENT_STATUS


class StatusFactoryHelper:
    AMOUNT = 9
    STATUS = 0
    STATUS_STEP = 100

    @classmethod
    def status(cls) -> int:
        cls.STATUS = cls.STATUS % (cls.STATUS_STEP * cls.AMOUNT)
        cls.STATUS += cls.STATUS_STEP
        return cls.STATUS


class StatusFactory(ModelFactory):
    __model__ = StatusModelWithRelations

    status = Use(StatusFactoryHelper.status)
    clients = Use(list)


factory_statuses_dto: Sequence[StatusModelWithRelations] = StatusFactory.batch(
    StatusFactoryHelper.AMOUNT,
    factory_use_construct=True,
)
assert len(factory_statuses_dto) >= 4, (
    'Ensure that the factory generates at least 4 statuses. It\'s required for'
    ' TestBulkCreate::test_with_some_not_unique.'
)
assert any(map(lambda s: s.status == DEFAULT_CLIENT_STATUS, factory_statuses_dto)), (
    f'Ensure that the client\'s default status ({DEFAULT_CLIENT_STATUS}) is generated.'
)
