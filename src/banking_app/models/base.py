from datetime import date
from datetime import datetime

from decimal import Decimal

from pydantic import BaseModel

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import DECIMAL

from typing import Annotated
from typing import Any
from typing import Type
from typing import TypeVar

from src.banking_app.conf import settings


date_today = Annotated[
    date, mapped_column(default=settings.get_date_today)
]
datetime_now = Annotated[
    datetime, mapped_column(default=settings.get_datetime_now)
]
decimal_8_2 = Annotated[
    Decimal, mapped_column(DECIMAL(precision=10, scale=2))
]
int_pk = Annotated[
    int, mapped_column(primary_key=True)
]
str_1 = Annotated[str, 1]
str_10 = Annotated[str, 10]
str_100 = Annotated[str, 100]
str_255 = Annotated[str, 255]


BaseModelType = TypeVar('BaseModelType', bound=BaseModel)


class Base(DeclarativeBase):
    repr_fields: tuple = tuple()
    type_annotation_map = {
        str_1: String(1),
        str_10: String(10),
        str_100: String(100),
        str_255: String(255),
    }

    def __str__(self) -> str:
        fields = ', '.join([
            f'{field}={getattr(self, field)}' for field in self.repr_fields
        ])
        return f'<{type(self).__name__}: {fields}>'

    def __repr__(self) -> str:
        return str(self)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        return super().__init__(*args, **kwargs)

    def to_dto_model(self, DTOModel: Type[BaseModelType]) -> BaseModelType:
        fields = DTOModel.model_fields.keys()
        data = {field: getattr(self, field) for field in fields}
        return DTOModel(**data)
