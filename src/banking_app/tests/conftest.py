import pytest
import subprocess

from typing import NamedTuple

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.session import sessionmaker

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
    """Before than tests session is started create DB."""

    # Drop DB if exist and then create DB.
    drop_db(engine)
    create_db(engine)
    message = f' Tests are started at: {test_settings.get_datetime_now()} '
    print('\n\n{:*^79}\n\n'.format(message))


@pytest.fixture(scope='session')
def session() -> Session:
    """Initialize context into sqlalchemy.orm.session_obj."""
    yield get_session_for_tests().send(None)


@pytest.fixture(scope='session', autouse=True)
def switch_db_for_fastapi_testing() -> None:
    """
    Switch used database into endpoints of application to test_db.

    Change all args of dependencies in endpoints from Depends(activate_session)
    to Depends(get_session_for_tests).

    Is required for example for tests where make changes of DB state, and we
    don't wont than main DB was changed.
    """
    banking_app.dependency_overrides[activate_session] = get_session_for_tests


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


def pytest_sessionfinish(session, exitstatus):
    """After than all tests are finished we drop tables and DB."""

    message = f' Tests are finished at: {test_settings.get_datetime_now()} '
    print('\n\n\n{:*^79}\n\n'.format(message))
    drop_db(engine)


def get_session_for_tests():
    with session_obj() as session:
        yield session


class UrlDbname(NamedTuple):
    url: str
    db_name: str


def get_url_db_name(engine: Engine) -> UrlDbname:
    """
    Return from passed engine valid to use into CMD url, without database name
    and without +<driver>.

    ```python
    # noqa: E501
    # Must be passed object of sqlalchemy.engine.base.Engine;

    print(engine.url)
    >>> postgresql+psycopg://username:***@localhost:5432/banking_test

    data = get_url_db_name(engine)
    str(data)
    >>> "UrlDbname(url='postgresql://postgres:postgres@localhost:5432', db_name='banking_test')"
    ```
    """
    url = engine.url
    url = url._replace(database=None, drivername=url.drivername.split('+')[0])
    url = url.render_as_string(hide_password=False)

    db_name = engine.url.database
    return UrlDbname(url=url, db_name=db_name)


def execute_shell_command(command: str, engine: Engine) -> None:
    result = subprocess.run(command, shell=True, capture_output=True)
    stdout = result.stdout.decode('utf8').strip().replace('\n', '\n\t')
    stderr = result.stderr.decode('utf8').strip().replace('\n', '\n\t')

    if result.returncode == 0:
        message = (
            f'\n\nSUCCESS:\n\tCommand was successfully executed!'
            f'\nCOMMAND:\n\t{command}'
            f'\n OUTPUT:\n\t{stdout}\n'
        )
        if stderr != '':
            message = message.rstrip() + f'\n   INFO:\n\t{stderr}\n'
        engine.logger.info(message)
    else:
        message = (
            f'\n\n  ERROR:\n\tIn time execution of command an error occurred.'
            f'\nCOMMAND:\n\t{command}'
            f'\n OUTPUT:\n\t{stderr}\n'
        )
        engine.logger.error(message)
        raise ProcessLookupError(message)


def create_db(engine: Engine) -> None:
    """Execute command in command line which create DB."""

    data = get_url_db_name(engine)

    create_db = f'psql {data.url} -c "CREATE DATABASE {data.db_name}"'
    execute_shell_command(command=create_db, engine=engine)


def drop_db(engine: Engine) -> None:
    """Execute command in command line which drop DB."""

    data = get_url_db_name(engine)

    drop_db = f'psql {data.url} -c "DROP DATABASE IF EXISTS {data.db_name} WITH (FORCE)"'  # noqa: E501
    execute_shell_command(command=drop_db, engine=engine)


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
