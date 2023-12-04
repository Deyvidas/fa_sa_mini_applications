from abc import ABC
from abc import abstractmethod

from typing import Any

from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select
from src.banking_app.models.base import Base


class AbstractManager(ABC):

    @property
    @abstractmethod
    def model(self) -> Base: ...


class BaseManager(AbstractManager):

    def create(self, session: Session, **kwargs) -> Base:
        instance = self.model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

    def filter(self, session: Session, **kwargs) -> list[Base]:
        query = select(self.model).filter_by(**kwargs)
        return session.execute(query).scalars().all()

    def get(self, session: Session, **kwargs) -> Base:
        query = select(self.model).filter_by(**kwargs)
        return session.execute(query).scalars().one()

    def bulk_create(
            self,
            session: Session,
            *,
            kwargs_list: list[dict[str, Any]],
    ) -> list[Base]:
        instances = [self.model(**kwargs) for kwargs in kwargs_list]
        session.add_all(instances)
        session.commit()
        return instances
