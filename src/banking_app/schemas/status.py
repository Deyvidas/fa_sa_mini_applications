from __future__ import annotations

from typing import Annotated
from typing import TYPE_CHECKING

from pydantic import Field

from src.banking_app.schemas import Base

if TYPE_CHECKING:
    from src.banking_app.schemas import BaseClientModel


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


class StatusModelWithRelations(BaseStatusModel):
    clients: list[BaseClientModel]


class StatusRetrieve(StatusModelWithRelations):
    ...


class StatusCreate(BaseStatusModel):
    ...


class StatusFullUpdate(BaseStatusModel):
    ...


class StatusPartialUpdate(BaseStatusModel):
    status: _status = Field(default=None)
    description: _description = Field(default=None)
