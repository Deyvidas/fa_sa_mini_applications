from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.banking_app.models.base import Base
from src.banking_app.models.base import int_pk
from src.banking_app.models.base import str_10
from src.banking_app.models.base import str_255
from src.banking_app.models.status import StatusDesc  # noqa: F401
from src.banking_app.types.client import Sex


class Client(Base):
    __tablename__ = 'client'

    client_id: Mapped[int_pk]
    full_name: Mapped[str_255]
    reg_date: Mapped[datetime]
    doc_num: Mapped[str_10]
    doc_series: Mapped[str_10]
    phone: Mapped[str_10]
    VIP_flag: Mapped[bool]
    birth_date: Mapped[datetime]
    sex: Mapped[Sex]

    status: Mapped[int] = mapped_column(
        ForeignKey(column='status_desc.status', ondelete='CASCADE')
    )
    client_status = relationship('StatusDesc', back_populates='clients')

    repr_fields = ('full_name', 'phone', 'sex')
