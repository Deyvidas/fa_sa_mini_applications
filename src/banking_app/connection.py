from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.banking_app.conf import settings


engine = create_engine(
    url=settings.DB_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    connect_args=settings.connect_args,
)


session = sessionmaker(bind=engine, expire_on_commit=False)


def activate_session():
    with session() as session_obj:
        return session_obj
