import pytest
import subprocess

from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session as OrmSession
from sqlalchemy.orm.session import sessionmaker

from src.banking_app.conf import test_settings
from src.banking_app.models.base import Base


Engine = create_engine(
    url=test_settings.DB_URL,
    echo=test_settings.ENGINE_ECHO,
    connect_args=test_settings.connect_args,
    pool_size=test_settings.ENGINE_POOL_SIZE,
    max_overflow=test_settings.ENGINE_MAX_OVERFLOW,
)


Session = sessionmaker(
    bind=Engine,
    autoflush=test_settings.SESSION_AUTOFLUSH,
    expire_on_commit=test_settings.SESSION_EXPIRE_ON_COMMIT,
)


def get_db_url_for_command_line(session: OrmSession) -> str:
    """
    Return from passed session valid url to use into CMD without database name.

    returned string: <drivername>://<username>:<password>@<host>:<port>

    ```python
    # Must be passed object of sqlalchemy.orm.session.Session;

    with Session() as session:
        url = get_db_url_for_command_line(session)
        print(url)

    >>> postgresql://username:not_hided_password@localhost:5432
    ```
    """
    url = session.bind.url
    url = url._replace(
        database=None,
        drivername=url.drivername.split('+')[0],
    ).render_as_string(hide_password=False)
    return url


def execute_shell_command(command: str, session: OrmSession) -> None:
    result = subprocess.run(command, shell=True, capture_output=True)

    if result.returncode == 0:
        stdout = result.stdout.decode('utf8').replace('\n', '\n\t')
        message = (
            f'\nSUCCESS:\n\tCommand was successfully executed!'
            f'\nCOMMAND:\n\t{command}'
            f'\n OUTPUT:\n\n{stdout}'
        )
        session.bind.logger.info(message)
    else:
        stderr = result.stderr.decode('utf8').replace('\n', '\n\t')
        message = (
            f'\n  ERROR:\n\tIn time execution of command an error occurred.'
            f'\nCOMMAND:\n\t{command}'
            f'\n OUTPUT:\n\t{stderr}'
        )
        session.bind.logger.error(message)
        raise ProcessLookupError(message)


# init_session before          (once when session is init - create and return session)  # noqa: E501
# ----db_create_drop before    (once when session is init - create db)
# --------create_tables before (before each test - create all tables into Base.metadata)  # noqa: E501
# ------------session before   (once when session is init - return session, pretty name for init_session)  # noqa: E501
# ----------------* tests run *
# ------------session after    (once when session is end - do nothing)
# --------create_tables after  (after each test - drop all tables in Base.metadata)  # noqa: E501
# ----db_create_drop after     (once when session is end - drop db)
# init_session after           (once when session is end - close session)


@pytest.fixture(scope='session')
def init_session() -> OrmSession:
    """Initialize context into sqlalchemy.orm.Session."""

    with Session() as session:
        yield session


@pytest.fixture(scope='session')
def db_create_drop(init_session) -> OrmSession:
    """Fixture create and drop database with name passed into engine.url:

    Before tests:
        - drop db with name in engine.url if exists;
        - and create new db with specified db_name into engine.url.

    After tests:
        - drop db with name in engine.url if exists;
    """

    url = get_db_url_for_command_line(init_session)
    db_name = init_session.bind.url.database

    connect = f'psql {url}'
    drop_db = f'{connect} -c "DROP DATABASE IF EXISTS {db_name}"'
    create_db = f'{connect} -c "CREATE DATABASE {db_name}"'

    # Closing connection to DB, else we can't drop DB because DB is used.
    Engine.dispose()
    execute_shell_command(command=drop_db, session=init_session)
    execute_shell_command(command=create_db, session=init_session)

    try:
        yield init_session
    except Exception:
        pass
    finally:
        # Closing connection to DB, else we can't drop DB because DB is used.
        Engine.dispose()
        execute_shell_command(command=drop_db, session=init_session)


@pytest.fixture(scope='session')
def session(db_create_drop):
    print('\n\n{:*^79}\n\n'.format(' starting tests '))
    yield db_create_drop
    print('\n\n\n{:*^79}\n\n'.format(' run of tests ended '))


@pytest.fixture(autouse=True)
def create_tables(session):
    Base.metadata.drop_all(bind=Engine)
    session.bind.logger.info('Base.metadata.drop_all OK!')
    Base.metadata.create_all(bind=Engine)
    session.bind.logger.info('Base.metadata.create_all OK!')

    try:
        yield
    except Exception:
        pass
    finally:
        Base.metadata.drop_all(bind=Engine)
        session.bind.logger.info('Base.metadata.drop_all OK!')
