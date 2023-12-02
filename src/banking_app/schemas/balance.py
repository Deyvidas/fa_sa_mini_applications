from datetime import datetime
from decimal import Decimal

from src.banking_app.schemas.base import Base


class BalancePostDTO(Base):
    current_amount: Decimal
    actual_flag: bool
    processed_datetime: datetime
    client_id: int


class BalanceGetDTO(BalancePostDTO):
    row_id: int
