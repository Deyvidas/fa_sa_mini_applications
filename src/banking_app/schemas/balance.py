from datetime import datetime

from decimal import Decimal

from pydantic import Field

from src.banking_app.conf import settings
from src.banking_app.schemas.base import Base
from src.banking_app.schemas.client import ClientRetrieve
from src.banking_app.types.general import MoneyAmount


class RowIdField(Base):
    row_id: int = Field(
        examples=[1234],
    )


class ActualFlagField(Base):
    actual_flag: bool


class ProcessedDateTimeField(Base):
    processed_datetime: datetime = Field(
        examples=[settings.get_datetime_now()],
    )


class ClientAsModelField(Base):
    client: ClientRetrieve


class ClientAsIntegerField(Base):
    client_id: int = Field(
        gt=0,
        examples=[24],
    )


class CurrAmountField(Base):
    current_amount: MoneyAmount = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
        examples=[Decimal(2) / Decimal(3)],  # 0.66(6) -> 0.67
    )


class BalanceRetrieve(
        ClientAsModelField,
        ProcessedDateTimeField,
        ActualFlagField,
        CurrAmountField,
        RowIdField,
):
    ...


class BalanceCreate(
        CurrAmountField,
        ClientAsIntegerField,
):
    ...
