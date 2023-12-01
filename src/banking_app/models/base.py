from pydantic import BaseModel

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column

from typing import Annotated
from typing import Type


int_pk = Annotated[int, mapped_column(primary_key=True)]
str_10 = Annotated[str, 10]
str_100 = Annotated[str, 100]
str_255 = Annotated[str, 255]


class Base(DeclarativeBase):
    repr_fields: tuple = tuple()
    type_annotation_map = {
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

    def to_dto_model(self, DTOModel: Type[BaseModel]) -> BaseModel:
        fields = DTOModel.model_fields.keys()
        data = {field: getattr(self, field) for field in fields}
        return DTOModel(**data)
