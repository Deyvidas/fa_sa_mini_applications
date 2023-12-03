from pydantic import Field

from src.banking_app.schemas.base import Base


class StatusDescDTO(Base):
    status: int = Field(
        gt=0,
        examples=[100],
    )
    description: str = Field(
        min_length=1,
        max_length=100,
        examples=['Some description of status.'],
    )
