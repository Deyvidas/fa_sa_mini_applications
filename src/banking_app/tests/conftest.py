import pytest
import subprocess

from typing import NamedTuple

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.session import sessionmaker

from src.banking_app.conf import test_settings
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
            f'\nSUCCESS:\n\tCommand was successfully executed!'
            f'\nCOMMAND:\n\t{command}'
            f'\n OUTPUT:\n\t{stdout}'
        )
        if stderr != '':
            message += f'\n   INFO:\n\t{stderr}'
        engine.logger.info(message)
    else:
        message = (
            f'\n  ERROR:\n\tIn time execution of command an error occurred.'
            f'\nCOMMAND:\n\t{command}'
            f'\n OUTPUT:\n\t{stderr}'
        )
        engine.logger.error(message)
        raise ProcessLookupError(message)


def pytest_sessionstart(session):
    """Before than tests session is started create DB and tables."""

    # Drop db if exist and then create db.
    drop_db(engine)
    create_db(engine)

    with session_obj() as connection:
        # Drop all tables if exists and then create tables.
        drop_tables(engine, connection)
        create_tables(engine, connection)

    message = f' Tests are started at: {test_settings.get_datetime_now()} '
    print('\n\n{:*^79}\n\n'.format(message))


@pytest.fixture(scope='session')
def session() -> Session:
    """Initialize context into sqlalchemy.orm.session_obj."""
    with session_obj() as session:
        yield session


@pytest.fixture(autouse=True)
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

    with session_obj() as connection:
        # Drop all tables.
        drop_tables(engine, connection)

    # Drop db.
    drop_db(engine)


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
    engine.logger.info('Base.metadata.create_all() OK!')


def drop_tables(engine: Engine, session: Session) -> None:
    """Drop all registered into Base.metadata tables."""

    session.commit()
    Base.metadata.drop_all(engine)
    session.commit()
    engine.logger.info('Base.metadata.drop_all() OK!')
