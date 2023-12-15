import pytest

from datetime import timedelta
from typing import Any

from src.banking_app.conf import test_settings
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.types.client import SexEnum


dates = dict(
    birth_date=test_settings.get_date_today() - timedelta(days=360),
    reg_date=test_settings.get_date_today(),
)


@pytest.fixture
def data_client(data_status) -> dict[str, Any]:
    """Fixture used into test_schemas."""
    status = StatusRetrieve(**data_status)
    data = dict(
        client_id=24,
        full_name="Zimin Denis Dmitrievich",
        birth_date=dates['birth_date'],
        sex=SexEnum.MALE,
        phone="9272554839",
        doc_num="92 31",
        doc_series="865734",
        reg_date=dates['reg_date'],
        VIP_flag=False,
        status=status,
    )
    return data
