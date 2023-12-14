from datetime import date

from decimal import Decimal

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
from src.banking_app.types.client import SexEnum

if TYPE_CHECKING:
    from src.banking_app.models.balance import Balance
    from src.banking_app.models.card import Card
    from src.banking_app.models.status import Status


class Client(Base):
    __tablename__ = 'client'
    repr_fields = ('full_name', 'phone', 'sex')
    VIP_if_balance = Decimal('900000')

    client_id: Mapped[int_pk]
    full_name: Mapped[str_255]
    reg_date: Mapped[date_today]
    doc_num: Mapped[str_10]
    doc_series: Mapped[str_10]
    phone: Mapped[str_10]
    VIP_flag: Mapped[bool] = mapped_column(default=False)
    birth_date: Mapped[date]
    sex: Mapped[SexEnum]

    status: Mapped[int] = mapped_column(
        ForeignKey(column='status_desc.status', ondelete='CASCADE'),
        default=200,
    )
    client_status: Mapped['Status'] = relationship(
        lazy='joined',
        back_populates='clients',
    )
    balances: Mapped[list['Balance']] = relationship(
        lazy='joined',
        back_populates='client',
        # Required for Balance.actual_flag updating when add new Balance.
        order_by='Balance.processed_datetime',
    )
    cards: Mapped[list['Card']] = relationship(
        lazy='joined',
        back_populates='client'
    )

    def actualize_balance(self):
        """
        Set `Balance.actual_flag=True` only for latest added balance into
        `Client.balances`, and change `Client.VIP_flag` in correspondence with
        latest `Balance.current_amount`.

        If Client hasn't actual Balance raise ValueError exception.
        """

        to_change: list['Balance'] = list(filter(
            lambda balance: balance.actual_flag is True, self.balances
        ))

        if len(to_change) == 0:
            raise ValueError(
                'Client with client_id={self.client_id} have`t actual balance.'
            )

        [setattr(balance, 'actual_flag', False) for balance in to_change[:-1]]
        self.actualize_vip_status(to_change[-1].current_amount)

    def actualize_vip_status(self, balance: Decimal):
        """
        Set Client.VIP_flag=True if latest actual Balance.current_amount great
        or equal than defined border.

        Set Client.VIP_flag=False if latest actual Balance.current_amount less
        than defined border.
        """

        if balance >= self.VIP_if_balance and self.VIP_flag is False:
            self.VIP_flag = True
        elif balance < self.VIP_if_balance and self.VIP_flag is True:
            self.VIP_flag = False
