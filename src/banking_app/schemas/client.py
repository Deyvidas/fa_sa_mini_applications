from datetime import date

from src.banking_app.schemas.base import Base
from src.banking_app.types.client import Sex


class ClientPostDTO(Base):
    full_name: str
    reg_date: date
    doc_num: str
    doc_series: str
    phone: str
    VIP_flag: bool
    birth_date: date
    sex: Sex
    status: int


class ClientGetDTO(ClientPostDTO):
    client_id: int
