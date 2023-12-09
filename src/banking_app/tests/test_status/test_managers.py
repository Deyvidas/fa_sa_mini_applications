import pytest

from pydantic import BaseModel

from sqlalchemy.orm.session import Session

from src.banking_app.models.status import StatusDesc
from src.banking_app.managers.status import StatusManager


class StatusDTO(BaseModel):
    status: int
    description: str


@pytest.fixture
def statuses() -> list[StatusDTO]:
    statuses = list()
    for i in range(1, 10):
        status = StatusDTO(
            status=i*100,
            description=f'Test description {i}',
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


class TestManager:
    manager = StatusManager()
    model = StatusDesc

    def test_create(
            self,
            session: Session,
            statuses: list[StatusDTO],
    ):
        status = statuses[0]

        create_stmt = self.manager.create(**status.model_dump())
        instance = session.scalar(create_stmt)  # type: StatusDesc
        session.commit()

        assert instance.status == status.status
        assert instance.description == status.description

    def test_bulk_create(
            self,
            session: Session,
            statuses: list[StatusDTO],
    ):
        list_kwargs = [status.model_dump() for status in statuses]
        bulk_create_stmt = self.manager.bulk_create(list_kwargs)
        instances = session.scalars(bulk_create_stmt).unique().all()  # type: list[StatusDesc]  # noqa: E501
        session.commit()

        assert len(instances) == len(statuses)

        instances_ord = sorted(instances, key=lambda instance: instance.status)
        statuses_ord = sorted(statuses, key=lambda status: status.status)

        for instance, status in zip(instances_ord, statuses_ord):
            assert instance.status == status.status
            assert instance.description == status.description

    def test_filter_without_params(
            self,
            session: Session,
            create_statuses: list[StatusDesc],
    ):
        statement = self.manager.filter()
        instances = session.scalars(statement).unique().all()
        assert len(instances) == len(create_statuses)
