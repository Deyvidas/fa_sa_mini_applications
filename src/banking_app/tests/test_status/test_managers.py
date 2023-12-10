from typing import Any

import pytest

from sqlalchemy.orm.session import Session

from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import StatusDesc
from src.banking_app.tests.test_status.conftest import StatusDTO


@pytest.mark.run(order=1.001)
@pytest.mark.usefixtures('create_and_drop_tables')
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
        instance: StatusDesc = session.scalar(create_stmt)
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
        instances: list[StatusDesc] = session.scalars(bulk_create_stmt).unique().all()  # noqa: E501
        session.commit()

        assert len(instances) == len(statuses)

        instances_ord = sorted(instances, key=lambda instance: instance.status)
        statuses_ord = sorted(statuses, key=lambda status: status.status)

        for instance, status in zip(instances_ord, statuses_ord):
            assert instance.status == status.status
            assert instance.description == status.description

    @pytest.mark.parametrize(
        argnames='filter_kwargs,filter_expr',
        argvalues=(
            pytest.param(
                dict(),
                'lambda s: True',
                id='filter()'
            ),
            pytest.param(
                dict(status=300),
                'lambda s: s.status == 300',
                id='filter(status=<int>)'
            ),
            pytest.param(
                dict(status__in=(100, 400, 900)),
                'lambda s: s.status in (100, 400, 900)',
                id='filter(status__in=(<int>, ...))'
            ),
            pytest.param(
                dict(
                    status=300,
                    description='Test description 300',
                ),
                (
                    'lambda s: s.status == 300 and '
                    's.description == "Test description 300"'
                ),
                id='filter(status=<int>, description=<str>)'
            ),
            pytest.param(
                dict(
                    status__in=(100, 400, 900),
                    description__in=('Test description 400', 'Test description 900'),  # noqa: E501
                ),
                (
                    'lambda s: s.status in (100, 400, 900) and '
                    's.description in ("Test description 400","Test description 900")'  # noqa: E501
                ),
                id='filter(status__in=(<int>, ...), description__in=(<str>, ...))'  # noqa: E501
            ),
        ),
    )
    def test_filter(
            self,
            session: Session,
            create_statuses: list[StatusDesc],
            filter_kwargs: dict[str, Any],
            filter_expr: str,
    ):
        statement = self.manager.filter(**filter_kwargs)
        instances: list[StatusDesc] = session.scalars(statement).unique().all()
        estimated_list = list(filter(eval(filter_expr), create_statuses))

        assert len(instances) == len(estimated_list)

        instances = sorted(instances, key=lambda s: s.status)
        estimated_list = sorted(estimated_list, key=lambda s: s.status)

        for instance, estimated in zip(instances, estimated_list):
            assert instance.status == estimated.status
            assert instance.description == estimated.description
