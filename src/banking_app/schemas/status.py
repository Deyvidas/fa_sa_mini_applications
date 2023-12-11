from typing import Annotated
from typing import Optional

from pydantic import Field

from src.banking_app.schemas.base import Base


Status = Annotated[
    int,
    Field(
        gt=0,
        examples=[100],
    )
]
Description = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        examples=['Some description of status.'],
    )
]


class StatusRequired(Base):
    status: Status


class DescriptionRequired(Base):
    description: Description


class DescriptionOptional(DescriptionRequired):
    description: Optional[Description] = None


class StatusRetrieve(
        DescriptionRequired,
        StatusRequired,
):
    ...


class StatusCreate(
        DescriptionRequired,
        StatusRequired,
):
    ...


class StatusFullUpdate(
        DescriptionRequired,
):
    ...


class StatusPartialUpdate(
        DescriptionOptional,
):
    ...
