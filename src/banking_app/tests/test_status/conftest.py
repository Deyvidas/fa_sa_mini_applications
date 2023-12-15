import pytest

from sqlalchemy.orm.session import Session

from typing import Sequence

from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import Status
from src.banking_app.schemas.status import StatusRetrieve


@pytest.fixture()
def data_status():
    """Fixture used into test_schemas."""
    default_data = dict(
        status=100,
        description='Test description',
    )
    return default_data


manager = StatusManager()


@pytest.fixture
def statuses() -> list[StatusRetrieve]:
    first = 100
    last = 900

    statuses: list[StatusRetrieve] = list()
    for i in range(first, last + 1, 100):
        status = StatusRetrieve(
            status=i,
            description=f'Test description {i}',
        )
        statuses.append(status)

    return statuses


@pytest.fixture
def created_statuses(
        session: Session,
        statuses: list[StatusRetrieve],
) -> Sequence[Status]:
    list_kwargs = [status.model_dump() for status in statuses]
    statement = manager.bulk_create(list_kwargs)
    instances = session.scalars(statement).unique().all()
    session.commit()

    assert len(instances) == len(statuses)
    return instances
