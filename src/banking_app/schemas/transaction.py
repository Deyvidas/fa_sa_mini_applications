from datetime import datetime
from decimal import Decimal

from src.banking_app.schemas.base import Base


class TransactionPostDTO(Base):
    trans_amount: Decimal
    trans_datetime: datetime
    processed_datetime: datetime
    card_number: str


class TransactionGetDTO(Base):
    trans_id: int
