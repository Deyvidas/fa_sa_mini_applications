from polyfactory.decorators import post_generated
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use

from typing import Sequence

from src.banking_app.schemas.status import StatusRetrieve


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
    __model__ = StatusRetrieve
    status = Use(StatusFactoryHelper.status)

    @post_generated
    @classmethod
    def description(cls, status: int) -> str:
        return f'Test description {status}'


factory_statuses_dto: Sequence[StatusRetrieve] = StatusFactory.batch(
    StatusFactoryHelper.AMOUNT,
    factory_use_construct=True,
)
