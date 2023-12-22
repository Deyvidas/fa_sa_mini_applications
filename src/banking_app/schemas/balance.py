from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pydantic import Field

from typing import Annotated
from typing import TYPE_CHECKING

from src.banking_app.conf import settings
from src.banking_app.schemas import Base
from src.banking_app.types.general import MoneyAmount

if TYPE_CHECKING:
    from src.banking_app.schemas import ClientRetrieve


_row_id = Annotated[
    int, Field(
        examples=[1234],
    )
]
_current_amount = Annotated[
    MoneyAmount, Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
        examples=[Decimal(2) / Decimal(3)],  # 0.66(6) -> 0.67
    )
]
_actual_flag = Annotated[
    bool, Field(
        examples=[False],
    )
]
_processed_datetime = Annotated[
    datetime, Field(
        examples=[settings.get_datetime_now()],
    )
]
_client_id = Annotated[
    int, Field(
        gt=0,
        examples=[24],
    )
]


class BaseBalanceModel(Base):
    row_id: _row_id
    current_amount: _current_amount
    actual_flag: _actual_flag
    processed_datetime: _processed_datetime
    client_id: _client_id

    client: ClientRetrieve


class BalanceRetrieve(BaseBalanceModel):
    client: ClientRetrieve = Field(default=None, exclude=True)


class BalanceCreate(BaseBalanceModel):
    row_id: _row_id = Field(default=None, exclude=True)
    actual_flag: _actual_flag = Field(default=None, exclude=True)
    processed_datetime: _processed_datetime = Field(default=None, exclude=True)

    client: ClientRetrieve = Field(default=None, exclude=True)
