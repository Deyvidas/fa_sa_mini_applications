from decimal import Decimal
from decimal import getcontext

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
