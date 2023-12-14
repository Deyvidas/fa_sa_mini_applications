from typing import Annotated

from pydantic import Field

from src.banking_app.schemas.base import Base


_status = Annotated[
    int, Field(
        gt=0,
        examples=[100],
    )
]
_description = Annotated[
    str, Field(
        min_length=1,
        max_length=100,
        examples=['Some description of status.'],
    )
]


class BaseStatusModel(Base):
    status: _status
    description: _description


class StatusRetrieve(BaseStatusModel):
    ...


class StatusCreate(BaseStatusModel):
    ...


class StatusFullUpdate(BaseStatusModel):
    status: _status = Field(default=None, exclude=True)


class StatusPartialUpdate(BaseStatusModel):
    status: _status = Field(default=None, exclude=True)
    description: _description = Field(default=None)
