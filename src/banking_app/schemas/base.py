from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from typing import Annotated


PositiveInt = Annotated[int, Field(gt=0)]


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)
