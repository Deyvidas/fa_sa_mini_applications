from typing import Optional
from sqlalchemy.sql.expression import select

from src.banking_app.connection import get_session
from src.banking_app.models.status import StatusDesc
from src.banking_app.managers.base import AbstractManager


class StatusManager(AbstractManager):
    model = StatusDesc
    session = get_session()

    def create(self, **kwargs) -> StatusDesc:
        instance = self.model(**kwargs)
        with self.session as session:
            session.add(instance)
            session.commit()
            return instance

    def filter(self, **kwargs) -> list[Optional[StatusDesc]]:
        query = select(self.model).filter_by(**kwargs)
        with self.session as session:
            return session.execute(query).scalars().all()

    def get(self, **kwargs) -> StatusDesc:
        query = select(self.model).filter_by(**kwargs)
        with self.session as session:
            return session.execute(query).scalars().one()
