import pytest

from abc import ABC
from fastapi.testclient import TestClient
from pydantic import BaseModel

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database  # type: ignore
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import drop_database
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.session import sessionmaker

from time import sleep

from typing import Any
from typing import Sequence
from typing import Type
from typing import TypeAlias

from src.banking_app.conf import test_settings
from src.banking_app.connection import activate_session
from src.banking_app.main import banking_app
from src.banking_app.managers.base import BaseManager
from src.banking_app.models.base import Base


engine = create_engine(
    url=test_settings.DB_URL,
    echo=test_settings.ENGINE_ECHO,
    connect_args=test_settings.connect_args,
    pool_size=test_settings.ENGINE_POOL_SIZE,
    max_overflow=test_settings.ENGINE_MAX_OVERFLOW,
)


session_obj = sessionmaker(
    bind=engine,
    autoflush=test_settings.SESSION_AUTOFLUSH,
    expire_on_commit=test_settings.SESSION_EXPIRE_ON_COMMIT,
)


def pytest_sessionstart(session):
    """Before than test session is started create DB."""
    create_db(engine)  # Drop DB if exist and then create DB.
    message = f' Tests are started at: {test_settings.get_datetime_now()} '
    print('\n{:*^79}\n'.format(message))


def pytest_sessionfinish(session, exitstatus):
    """Drop database when test session is ended."""
    message = f' Tests are finished at: {test_settings.get_datetime_now()} '
    print('\n\n{:*^79}\n'.format(message))
    drop_db(engine)


@pytest.fixture(scope='session')
def session():
    """Initialize context of sqlalchemy.orm.Session."""
    with session_obj() as session:
        yield session


@pytest.fixture(scope='session', autouse=True)
def switch_used_session_in_dependencies(session) -> None:
    """Switch used session into endpoints depends."""

    def test_session():
        yield session

    banking_app.dependency_overrides[activate_session] = test_session


@pytest.fixture
def create_and_drop_tables(session: Session):

    try:
        engine.echo = False
        create_tables(engine, session)
        engine.echo = test_settings.ENGINE_ECHO
        yield
        engine.echo = False
        drop_tables(engine, session)
        engine.echo = test_settings.ENGINE_ECHO
    except Exception:
        pass
    finally:
        engine.echo = test_settings.ENGINE_ECHO


def create_db(engine: Engine) -> None:
    """Execute command in command line which create DB."""

    drop_db(engine)
    sleep(1)  # Sleep is required!
    create_database(engine.url)
    engine.logger.info(f'|| DB CREATED SUCCESSFULLY (url={engine.url}) ||')


def drop_db(engine: Engine) -> None:
    """Execute command in command line which drop DB."""

    if database_exists(engine.url):
        drop_database(engine.url)
        engine.logger.info(f'|| DB DROPPED SUCCESSFULLY (url={engine.url}) ||')


def create_tables(engine: Engine, session: Session) -> None:
    """Create all registered into Base.metadata tables."""

    drop_tables(engine, session)
    Base.metadata.create_all(engine)
    session.commit()

    message = '\n{:*^79}'.format(' Base.metadata.create_all() OK! ')
    engine.logger.info(message)


def drop_tables(engine: Engine, session: Session) -> None:
    """Drop all registered into Base.metadata tables."""

    session.rollback()
    Base.metadata.drop_all(engine)
    session.commit()

    message = '\n{:*^79}'.format(' Base.metadata.drop_all() OK! ')
    engine.logger.info(message)


class BaseTest(ABC):
    client: TestClient
    manager: BaseManager
    model_dto: Type[BaseModel]
    model_orm: Type[Base]
    ord_by_default: str
    prefix: str

    DataType: TypeAlias = Base | BaseModel | dict[str, Any]

    @property
    def fields(self) -> Sequence[str]:
        fields = self.model_orm.__table__.columns._all_columns
        return [field.name for field in fields]

    def not_found_msg(self, **kwargs) -> str:
        details = ', '.join([f'{k}={v}' for k, v in kwargs.items()])
        return f'{self.model_orm.__name__} with {details} not found.'

    def not_unique_msg(self, **kwargs) -> str:
        details = ', '.join([f'{k}={v}' for k, v in kwargs.items()])
        return f'{self.model_orm.__name__} with {details} already exists.'

    def empty_patch_body(self, **kwargs) -> str:
        details = ', '.join([f'{k}={v}' for k, v in kwargs.items()])
        return (
            f'{self.model_orm.__name__} with {details} can\'t be updated,'
            ' received empty body, change at least value of one field.'
        )

    def compare_obj_before_after[T: DataType, S: Sequence[str]](
            self,
            before: T,
            after: T,
            *,
            exclude: S | None = None,
            fields: S | None = None,
    ):
        self.compare_list_before_after(
            before=[before],
            after=[after],
            exclude=exclude,
            fields=fields,
        )

    def compare_list_before_after[T: DataType, S: Sequence[str]](
            self,
            before: Sequence[T],
            after: Sequence[T],
            *,
            exclude: S | None = None,
            fields: S | None = None,
    ):
        assert len(before) == len(after) and len(before) > 0

        # Convert dict into an instance to use getattr.
        if isinstance(before[0], dict):
            before = [self.model_orm(**kwargs) for kwargs in before]            # type: ignore
        if isinstance(after[0], dict):
            after = [self.model_orm(**kwargs) for kwargs in after]              # type: ignore

        # By default we sort by status, but it can be excluded.
        fields = self._get_final_field_set(exclude, fields)
        ord_by = self.ord_by_default
        if ord_by not in fields:
            ord_by = fields[0]

        if len(before) > 1:
            before = sorted(before, key=lambda b: getattr(b, ord_by))
            after = sorted(after, key=lambda a: getattr(a, ord_by))

        for b, a in zip(before, after):
            for field in fields:
                assert getattr(a, field) == getattr(b, field)

    def _get_final_field_set[S: Sequence[str]](
            self,
            exclude: S | None,
            fields: S | None,
    ) -> S:
        _fields = self.fields
        if fields is not None and len(fields) > 0:
            _fields = fields
        if exclude is not None and len(exclude) > 0:
            diff = set(_fields) - set(exclude)
            if len(diff) != 0:
                return list(diff)                                               # type: ignore
        return list(_fields)                                                    # type: ignore
