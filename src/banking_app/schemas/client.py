from datetime import datetime

from src.banking_app.schemas.base import Base
from src.banking_app.types.client import Sex


class ClientCreateDTO(Base):
    full_name: str
    reg_date: datetime
    doc_num: str
    doc_series: str
    phone: str
    VIP_flag: bool
    birth_date: datetime
    sex: Sex
    status: int


class ClientFetchDTO(ClientCreateDTO):
    client_id: int
