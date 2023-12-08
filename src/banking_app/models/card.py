from datetime import date
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.types import String

from typing import TYPE_CHECKING

from src.banking_app.models.base import Base
from src.banking_app.types.card import CardType

if TYPE_CHECKING:
    from src.banking_app.models.client import Client
    from src.banking_app.models.transaction import Transaction


class Card(Base):
    __tablename__ = 'card'
    repr_fields = ('card_number', 'card_type', 'open_date', 'close_date')

    card_number = mapped_column(String(16), primary_key=True)
    card_type: Mapped[CardType]
    open_date: Mapped[date]
    close_date: Mapped[date]
    processed_datetime: Mapped[datetime]

    client_id: Mapped[int] = mapped_column(
        ForeignKey('client.client_id', ondelete='CASCADE'),
    )
    client: Mapped['Client'] = relationship(
        lazy='joined',
        back_populates='cards',
    )
    transactions: Mapped[list['Transaction']] = relationship(
        lazy='joined',
        back_populates='card',
    )
