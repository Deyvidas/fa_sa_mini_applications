from typing import Any

import pytest

from sqlalchemy.orm.session import Session

from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import Status
from src.banking_app.schemas.status import StatusRetrieve


@pytest.mark.run(order=1.001)
@pytest.mark.usefixtures('create_and_drop_tables')
class TestManager:
    manager = StatusManager()
    model = Status

    def test_create(
            self,
            session: Session,
            statuses: list[StatusRetrieve],
    ):
        status = statuses[0]

        create_stmt = self.manager.create(**status.model_dump())
        instance: Status = session.scalar(create_stmt)
        session.commit()

        assert instance.status == status.status
        assert instance.description == status.description

    def test_bulk_create(
            self,
            session: Session,
            statuses: list[StatusRetrieve],
    ):
        list_kwargs = [status.model_dump() for status in statuses]
        bulk_create_stmt = self.manager.bulk_create(list_kwargs)
        instances: list[Status] = session.scalars(bulk_create_stmt).unique().all()  # noqa: E501
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
                id='filter without conditions'
            ),
            pytest.param(
                dict(status=300),
                'lambda s: s.status == 300',
                id='filter with single base condition'
            ),
            pytest.param(
                dict(status__in=(100, 400, 900)),
                'lambda s: s.status in (100, 400, 900)',
                id='filter with single IN condition'
            ),
            pytest.param(
                dict(status__between=(200, 400)),
                'lambda s: s.status in range(200, 401)',
                id='filter with single BETWEEN condition'
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
                id='filter with multi base conditions'
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
                id='filter with multi IN conditions'
            ),
        ),
    )
    def test_filter(
            self,
            session: Session,
            created_statuses: list[Status],
            filter_kwargs: dict[str, Any],
            filter_expr: str,
    ):
        statement = self.manager.filter(**filter_kwargs)
        instances: list[Status] = session.scalars(statement).unique().all()
        estimated_list = list(filter(eval(filter_expr), created_statuses))

        assert len(instances) == len(estimated_list)

        instances = sorted(instances, key=lambda s: s.status)
        estimated_list = sorted(estimated_list, key=lambda s: s.status)

        for instance, estimated in zip(instances, estimated_list):
            assert instance.status == estimated.status
            assert instance.description == estimated.description

    @pytest.mark.parametrize(
        argnames='condition,values',
        argvalues=(
            pytest.param(
                dict(status=300),
                dict(description='New description.'),
                id='update single object'
            ),
            pytest.param(
                dict(status__between=(200, 500)),
                dict(description='New description.'),
                id='update multiple object'
            ),
        ),
    )
    def test_update(
            self,
            session: Session,
            created_statuses: list[Status],
            condition: dict[str, Any],
            values: dict[str, Any],
    ):
        # Count amount of statuses which must be updated.
        statement = self.manager.filter(**condition)
        count = len(session.scalars(statement).unique().all())

        statement = self.manager.update(where=condition, set_value=values)
        updated: list[Status] = session.scalars(statement).unique().all()
        session.commit()
        assert len(updated) == count

        # Make sure than objects are updated in DB.
        updated_statuses = [u.status for u in updated]
        statement = self.manager.filter(**dict(status__in=updated_statuses))
        updated = session.scalars(statement).unique().all()
        for field, new_value in values.items():
            for status in updated:
                assert getattr(status, field) == new_value
