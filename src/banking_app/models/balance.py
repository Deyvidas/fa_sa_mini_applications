from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.banking_app.models.base import Base
from src.banking_app.models.base import decimal_8_2
from src.banking_app.models.base import int_pk
from src.banking_app.models.client import Client  # noqa: F401


class Balance(Base):
    __tablename__ = 'balance'
    repr_fields = ('row_id', 'actual_flag', 'client_id')

    row_id: Mapped[int_pk]
    current_amount: Mapped[decimal_8_2]
    actual_flag: Mapped[bool]
    processed_datetime: Mapped[datetime]

    client_id: Mapped[int] = mapped_column(
        ForeignKey('client.client_id', ondelete='CASCADE')
    )
    client = relationship('Client', back_populates='balances', lazy='joined')
