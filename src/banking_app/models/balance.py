from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from typing import TYPE_CHECKING

from src.banking_app.models.base import Base
from src.banking_app.models.base import datetime_now
from src.banking_app.models.base import decimal_8_2
from src.banking_app.models.base import int_pk

if TYPE_CHECKING:
    from src.banking_app.models.client import Client


class Balance(Base):
    __tablename__ = 'balance'
    repr_fields = ('row_id', 'actual_flag', 'client_id')

    row_id: Mapped[int_pk]
    current_amount: Mapped[decimal_8_2]
    actual_flag: Mapped[bool] = mapped_column(default=True)
    # Value of processed_datetime field cant be assigned manually!
    # Value of this field is used to sort Client.balances.
    processed_datetime: Mapped[datetime_now]

    client_id: Mapped[int] = mapped_column(
        ForeignKey('client.client_id', ondelete='CASCADE'),
    )
    client: Mapped['Client'] = relationship(
        back_populates='balances',
    )
