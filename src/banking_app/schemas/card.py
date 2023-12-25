from __future__ import annotations

from datetime import date
from datetime import datetime

from pydantic import Field
from pydantic import model_validator
from pydantic_core import PydanticCustomError

from typing import Annotated
from typing import TYPE_CHECKING

from src.banking_app.schemas import Base
from src.banking_app.types.card import CardType

if TYPE_CHECKING:
    from src.banking_app.schemas import BaseClientModel
    from src.banking_app.schemas import BaseTransactionModel


_card_number = Annotated[
    str, Field(
        min_length=16,
        max_length=16,
        examples=['4188680335268618'],
    )
]
_card_type = Annotated[
    CardType, Field(
        examples=[CardType.DEBIT],
    )
]
_open_date = Annotated[
    date, Field()
]
_close_date = Annotated[
    date, Field()
]
_processed_datetime = Annotated[
    datetime, Field()
]
_client_id = Annotated[
    int, Field(
        gt=0,
        examples=[12345]
    )
]


class BaseCardModel(Base):
    card_number: _card_number
    card_type: _card_type
    open_date: _open_date
    close_date: _close_date
    processed_datetime: _processed_datetime
    client_id: _client_id

    @model_validator(mode='after')
    def validate_model(self):
        self.close_date_cant_be_earlier_than_open_date()
        return self

    def close_date_cant_be_earlier_than_open_date(self):
        if self.open_date <= self.close_date:
            return
        raise PydanticCustomError(
            'invalid_close_date',
            'Close date can`t be earlier than open date.',
        )


class CardModelWithRelations(BaseCardModel):
    client: BaseClientModel
    transactions: list[BaseTransactionModel]


class CardRetrieve(CardModelWithRelations):
    ...


class CardCreate(BaseCardModel):
    ...
