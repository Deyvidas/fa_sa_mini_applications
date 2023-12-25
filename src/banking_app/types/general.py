from decimal import Decimal
from decimal import getcontext

from enum import Enum
from pydantic import PlainSerializer

from typing import Annotated


getcontext().prec = 2
MoneyAmount = Annotated[
    Decimal,
    PlainSerializer(
        lambda x: float(x),
        return_type=float,
        when_used='json',
    )
]


class BaseEnum(Enum):
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'{type(self).__name__}.{self.name}'
