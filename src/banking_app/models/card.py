from datetime import date
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.types import String

from src.banking_app.models.base import Base
from src.banking_app.models.client import Client  # noqa: F401
from src.banking_app.types.card import CardType


class Card(Base):
    __tablename__ = 'card'
    repr_fields = ('card_number', 'card_type', 'open_date', 'close_date')

    card_number = mapped_column(String(16), primary_key=True)
    card_type: Mapped[CardType]
    open_date: Mapped[date]
    close_date: Mapped[date]
    processed_datetime: Mapped[datetime]

    client_id: Mapped[int] = mapped_column(
        ForeignKey('client.client_id', ondelete='CASCADE')
    )
    client = relationship(
        'Client',
        back_populates='cards',
        lazy='joined',
    )
    transactions = relationship(
        'Transaction',
        back_populates='card',
        lazy='joined',
    )
