from pydantic import Field

from src.banking_app.schemas.base import Base


class StatusField(Base):
    status: int = Field(
        gt=0,
        examples=[100],
    )


class DescriptionField(Base):
    description: str = Field(
        min_length=1,
        max_length=100,
        examples=['Some description of status.'],
    )


class StatusRetrieve(
        DescriptionField,
        StatusField,
):
    ...


class StatusCreate(
        DescriptionField,
        StatusField,
):
    ...


class StatusUpdate(
        DescriptionField,
):
    ...
