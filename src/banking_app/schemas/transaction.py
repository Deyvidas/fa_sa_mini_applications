from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pydantic import Field

from typing import Annotated
from typing import TYPE_CHECKING

from src.banking_app.schemas import Base

if TYPE_CHECKING:
    from src.banking_app.schemas import CardDTO


_trans_id = Annotated[
    int, Field(
        examples=[1234],
    )
]
_trans_amount = Annotated[
    Decimal, Field()
]
_trans_datetime = Annotated[
    datetime, Field()
]
_processed_datetime = Annotated[
    datetime, Field()
]
_card_number = Annotated[
    str, Field()
]


class BaseTransactionModel(Base):
    trans_id: _trans_id
    trans_amount: _trans_amount
    trans_datetime: _trans_datetime
    processed_datetime: _processed_datetime
    card_number: _card_number

    card: CardDTO


class TransactionPostDTO(BaseTransactionModel):
    trans_id: _trans_id = Field(default=None, exclude=True)


class TransactionGetDTO(TransactionPostDTO):
    card: CardDTO = Field(default=None, exclude=True)
