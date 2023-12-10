import pytest

from pydantic import BaseModel

from sqlalchemy.orm.session import Session

from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import Status


manager = StatusManager()


class StatusDTO(BaseModel):
    status: int
    description: str


@pytest.fixture
def statuses() -> list[StatusDTO]:
    first = 1
    last = 9
    statuses = list()
    for i in range(first, last+1):
        num = i * 100
        status = StatusDTO(
            status=num,
            description=f'Test description {num}',
        )
        statuses.append(status)

    assert len(statuses) == last
    return statuses


@pytest.fixture
def create_statuses(
        session: Session,
        statuses: list[StatusDTO],
) -> list[Status]:
    list_kwargs = [status.model_dump() for status in statuses]
    statement = manager.bulk_create(list_kwargs)
    session.scalars(statement).unique().all()
    session.commit()

    statement = manager.filter()
    instances = session.scalars(statement).unique().all()
    assert len(instances) == len(statuses)
    return instances
