from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from typing import TYPE_CHECKING

from src.banking_app.models.base import Base
from src.banking_app.models.base import date_today
from src.banking_app.models.base import int_pk
from src.banking_app.models.base import str_10
from src.banking_app.models.base import str_255
from src.banking_app.types.client import Sex

if TYPE_CHECKING:
    from src.banking_app.models.balance import Balance
    from src.banking_app.models.card import Card
    from src.banking_app.models.status import StatusDesc


class Client(Base):
    __tablename__ = 'client'
    repr_fields = ('full_name', 'phone', 'sex')

    client_id: Mapped[int_pk]
    full_name: Mapped[str_255]
    reg_date: Mapped[date_today]
    doc_num: Mapped[str_10]
    doc_series: Mapped[str_10]
    phone: Mapped[str_10]
    VIP_flag: Mapped[bool] = mapped_column(default=False)
    birth_date: Mapped[date]
    sex: Mapped[Sex]

    status: Mapped[int] = mapped_column(
        ForeignKey(column='status_desc.status', ondelete='CASCADE'),
        default=200,
    )
    client_status: Mapped['StatusDesc'] = relationship(
        back_populates='clients'
    )
    balances: Mapped[list['Balance']] = relationship(
        back_populates='client',
        # Required for Balance.actual_flag updating when add new Balance.
        order_by='Balance.processed_datetime',
    )
    cards: Mapped[list['Card']] = relationship(
        back_populates='client'
    )
