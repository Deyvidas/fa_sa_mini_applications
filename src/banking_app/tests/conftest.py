import pytest

from time import sleep

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.session import sessionmaker

from sqlalchemy_utils import create_database  # type: ignore
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import drop_database

from src.banking_app.conf import test_settings
from src.banking_app.connection import activate_session
from src.banking_app.main import banking_app
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
def create_and_drop_tables(session: Session) -> None:
    engine.echo = False  # OFF echo between test because is cumbersome.

    try:
        drop_tables(engine, session)
        create_tables(engine, session)
        yield
        drop_tables(engine, session)
    except Exception:
        pass
    finally:
        engine.echo = test_settings.ENGINE_ECHO  # After reset value.


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

    session.commit()
    Base.metadata.create_all(engine)
    session.commit()
    message = '\n{:*^79}'.format(' Base.metadata.create_all() OK! ')
    engine.logger.info(message)


def drop_tables(engine: Engine, session: Session) -> None:
    """Drop all registered into Base.metadata tables."""

    session.commit()
    Base.metadata.drop_all(engine)
    session.commit()
    message = '\n{:*^79}'.format(' Base.metadata.drop_all() OK! ')
    engine.logger.info(message)
