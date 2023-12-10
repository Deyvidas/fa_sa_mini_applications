import pytest

from pydantic import BaseModel

from sqlalchemy.orm.session import Session

from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import StatusDesc


class StatusDTO(BaseModel):
    status: int
    description: str


@pytest.fixture
def statuses() -> list[StatusDTO]:
    statuses = list()
    for i in range(1, 10):
        num = i * 100
        status = StatusDTO(
            status=num,
            description=f'Test description {num}',
        )
        statuses.append(status)
    return statuses


@pytest.fixture
def create_statuses(
        session: Session,
        statuses: list[StatusDTO],
) -> list[StatusDesc]:
    list_kwargs = [status.model_dump() for status in statuses]
    statement = StatusManager().bulk_create(list_kwargs)
    instances = session.scalars(statement).unique().all()
    session.commit()
    return instances
