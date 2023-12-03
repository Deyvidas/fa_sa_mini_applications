from pydantic import BaseModel
from pydantic import Field

from typing import Annotated


PositiveInt = Annotated[int, Field(gt=0)]


class Base(BaseModel):
    ...
