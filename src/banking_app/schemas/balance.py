from datetime import datetime

from decimal import Decimal

from pydantic import ConfigDict
from pydantic import Field

from typing import Union

from src.banking_app.conf import settings
from src.banking_app.models.client import Client
from src.banking_app.schemas.base import Base
from src.banking_app.schemas.client import ClientGetDTO
from src.banking_app.types.general import MoneyAmount


class BalancePostDTO(Base):

    current_amount: MoneyAmount = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
        examples=[Decimal(2) / Decimal(3)],  # 0.66(6) -> 0.67
    )
    client_id: int = Field(
        gt=0,
        examples=[24],
    )


class BalanceGetDTO(BalancePostDTO):
    client_id: int = Field(exclude=True)
    row_id: int
    actual_flag: bool
    processed_datetime: datetime = Field(
        examples=[settings.get_now_datetime()],
    )
    client: Union[ClientGetDTO, Client]

    model_config = ConfigDict(arbitrary_types_allowed=True)
