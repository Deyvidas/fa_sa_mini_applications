from datetime import date
from datetime import datetime

from pydantic import Field
from pydantic import model_validator
from pydantic_core import PydanticCustomError

from re import fullmatch

from src.banking_app.schemas.base import Base
from src.banking_app.types.card import CardType


class CardDTO(Base):
    card_number: str = Field(
        min_length=16,
        max_length=16,
        example='4188680335268618',
    )
    card_type: CardType
    open_date: date
    close_date: date
    processed_datetime: datetime
    client_id: int = Field(
        gt=0,
        example=12345
    )

    @model_validator(mode='after')
    def validate_model(self):
        self.card_number_must_contain_only_digits()
        self.close_date_cant_be_earlier_than_open_date()
        return self

    def card_number_must_contain_only_digits(self):
        if fullmatch(r'^[\d]{16}$', self.card_number) is not None:
            return
        raise PydanticCustomError(
            'invalid_card_number',
            'Passed card number is invalid.',
        )

    def close_date_cant_be_earlier_than_open_date(self):
        if self.open_date <= self.close_date:
            return
        raise PydanticCustomError(
            'invalid_close_date',
            'Close date can`t be earlier than open date.',
        )
