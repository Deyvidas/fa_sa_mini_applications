from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from typing import TYPE_CHECKING

from src.banking_app.models.base import Base
from src.banking_app.models.base import int_pk
from src.banking_app.models.base import str_100

if TYPE_CHECKING:
    from src.banking_app.models.client import Client


class StatusDesc(Base):
    __tablename__ = 'status_desc'
    repr_fields = ('status', 'description')

    status: Mapped[int_pk]
    description: Mapped[str_100]

    clients: Mapped['Client'] = relationship(
        back_populates='client_status',
    )
