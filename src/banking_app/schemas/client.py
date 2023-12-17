from datetime import date

from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator
from pydantic_core import PydanticCustomError

from typing import Annotated

from src.banking_app.conf import settings
from src.banking_app.schemas.base import Base
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.types.client import SexEnum


_client_id = Annotated[
    int, Field(
        gt=0,
        examples=[24],
    )
]
_full_name = Annotated[
    str, Field(
        min_length=10,
        max_length=255,
        examples=['Zimin Denis Dmitrievich'],
        pattern=r'^[A-Z][a-z]+( [A-Z][a-z]+){2}$',
    )
]
_birth_date = Annotated[
    date, Field(
        examples=[settings.get_date_today()],
        description='Birth date cannot be after today.',
    )
]
_sex = Annotated[
    SexEnum, Field(
        examples=[SexEnum.MALE],
    )
]
_phone = Annotated[
    str, Field(
        min_length=10,
        max_length=10,
        examples=['9272554839', '8495774411'],
        pattern=r'^[\d]{10}$',
    )
]
_doc_num = Annotated[
    str, Field(
        min_length=5,
        max_length=5,
        examples=['92 31'],
        pattern=r'^[\d]{2} [\d]{2}$',
    )
]
_doc_series = Annotated[
    str, Field(
        min_length=6,
        max_length=6,
        examples=['865734'],
        pattern=r'^[\d]{6}$',
    )
]
_reg_date = Annotated[
    date, Field(
        examples=[settings.get_date_today()],
        description='Registration date cannot be after today.',
    )
]
_VIP_flag = Annotated[
    bool, Field(
        examples=[False],
    )
]
_status_number = Annotated[
    int, Field(
        gt=0,
        examples=[100],
    )
]
_status_model = Annotated[
    StatusRetrieve, Field()
]


class BaseClientModel(Base):
    client_id: _client_id
    full_name: _full_name
    birth_date: _birth_date
    sex: _sex
    phone: _phone
    doc_num: _doc_num
    doc_series: _doc_series
    reg_date: _reg_date
    VIP_flag: _VIP_flag
    status: _status_number
    client_status: _status_model

    @field_validator('birth_date')
    @classmethod
    def birth_date_not_in_future(cls, birth_date: date):
        if birth_date <= (today := settings.get_date_today()):
            return birth_date
        raise PydanticCustomError(
            'invalid birth date',
            'Birth date cannot be after {today}.',
            dict(today=today),
        )

    @field_validator('reg_date')
    @classmethod
    def reg_date_not_in_future(cls, reg_date: date):
        if reg_date <= (today := settings.get_date_today()):
            return reg_date
        raise PydanticCustomError(
            'invalid registration date',
            'Registration date cannot be after {today}.',
            dict(today=today)
        )

    @model_validator(mode='after')
    def registration_cant_be_earlier_than_birth_date(self):
        # reg_date is optional in some models and is excluded.
        if self.reg_date is None and self.model_fields['reg_date'].exclude is True:
            return self

        if (bd := self.birth_date) <= (rd := self.reg_date):
            return self
        raise PydanticCustomError(
            'invalid combination of birth and registration data',
            'Registration date ({rd}) cannot be before the client birth date ({bd}).',
            dict(rd=rd, bd=bd)
        )


class ClientRetrieve(BaseClientModel):
    status: _status_number = Field(default=None, exclude=True)


class ClientCreate(BaseClientModel):
    client_id: _client_id = Field(default=None, exclude=True)
    reg_date: _reg_date = Field(default=None, exclude=True)
    VIP_flag: _VIP_flag = Field(default=None, exclude=True)
    status: _status_number = Field(default=None, exclude=True)
    client_status: _status_model = Field(default=None, exclude=True)


class ClientFullUpdate(BaseClientModel):
    client_id: _client_id = Field(default=None, exclude=True)
    reg_date: _reg_date = Field(default=None, exclude=True)
    VIP_flag: _VIP_flag = Field(default=None, exclude=True)
    client_status: _status_model = Field(default=None, exclude=True)


class ClientPartialUpdate(BaseClientModel):
    client_id: _client_id = Field(default=None, exclude=True)
    full_name: _full_name = Field(default=None)
    birth_date: _birth_date = Field(default=None)
    sex: _sex = Field(default=None)
    phone: _phone = Field(default=None)
    doc_num: _doc_num = Field(default=None)
    doc_series: _doc_series = Field(default=None)
    reg_date: _reg_date = Field(default=None, exclude=True)
    VIP_flag: _VIP_flag = Field(default=None, exclude=True)
    status: _status_number = Field(default=None)
    client_status: _status_model = Field(default=None, exclude=True)
