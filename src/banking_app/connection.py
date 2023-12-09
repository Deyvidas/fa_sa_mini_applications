from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.banking_app.conf import settings


Engine = create_engine(
    url=settings.DB_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    connect_args=settings.connect_args,
)


Session = sessionmaker(
    bind=Engine,
    autoflush=True,  # Call method session.flush() after session.execute(stmt);
    expire_on_commit=False,
)


def activate_session():
    with Session() as session:
        return session


# session.flush() - make mock query to DB and load object fully, for example
# if object is created it hasn't pk, but after session.autoflush() pk is
# assigned and all related objects too, for example, created new object with
# relation with another object by pk, and before than session.flush() is called
# we can access only to assigned value to FK field, and if try to access to
# back_populate attribute happen exception, but after session.flush(), into
# back_populate attribute of object appear related object with ID placed in FK.
# IMPORTANT session.flush() imitate query to DB, but doesn't do real query.
