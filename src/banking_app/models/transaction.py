from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from typing import TYPE_CHECKING

from src.banking_app.models.base import Base
from src.banking_app.models.base import decimal_8_2
from src.banking_app.models.base import int_pk

if TYPE_CHECKING:
    from src.banking_app.models.card import Card


class Transaction(Base):
    __tablename__ = 'transaction'
    repr_fields = ('trans_id', 'trans_amount')

    trans_id: Mapped[int_pk]
    trans_amount: Mapped[decimal_8_2]
    trans_datetime: Mapped[datetime]
    processed_datetime: Mapped[datetime]

    card_number: Mapped[str] = mapped_column(
        ForeignKey('card.card_number', ondelete='CASCADE')
    )
    card: Mapped['Card'] = relationship(
        lazy='joined',
        back_populates='transactions',
    )
