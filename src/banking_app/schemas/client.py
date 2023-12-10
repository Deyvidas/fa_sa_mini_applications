from datetime import date

from pydantic import Field
from pydantic import field_validator

from typing import Union

from src.banking_app.conf import settings
from src.banking_app.schemas.base import Base
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.types.client import Sex


class ClientPostDTO(Base):
    full_name: str = Field(
        min_length=10,
        max_length=255,
        examples=['Zimin Denis Dmitrievich'],
        pattern=r'^[A-Z][a-z]+( [A-Z][a-z]+){2}$',
    )
    doc_num: str = Field(
        min_length=5,
        max_length=5,
        examples=['92 31'],
        pattern=r'^[\d]{2} [\d]{2}$',
    )
    doc_series: str = Field(
        min_length=6,
        max_length=6,
        examples=['865734'],
        pattern=r'^[\d]{6}$',
    )
    phone: str = Field(
        min_length=10,
        max_length=10,
        examples=['9272554839', '8495774411'],
        pattern=r'^[\d]{10}$',
    )
    birth_date: date = Field(
        examples=[settings.get_date_today()],
        description='Birth date can`t be after than today.',
    )
    sex: Sex

    @field_validator('birth_date', mode='after')
    @classmethod
    def birth_date_not_in_future(cls, birth_date: date):
        if birth_date <= (today := settings.get_date_today()):
            return birth_date
        raise ValueError(f'Birth date can`t be after than {today}.')


class ClientGetDTO(ClientPostDTO):
    client_id: int = Field(
        gt=0,
        examples=[24],
    )
    reg_date: date = Field(
        examples=[settings.get_date_today()],
    )
    VIP_flag: bool = Field(
        examples=[False],
    )
    status: Union[StatusRetrieve, int]

    @field_validator('reg_date', mode='after')
    @classmethod
    def reg_date_not_in_future(cls, reg_date: date):
        if reg_date <= (today := settings.get_date_today()):
            return reg_date
        raise ValueError(f'Registration date can`t be after than {today}.')
