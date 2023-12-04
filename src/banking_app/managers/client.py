from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select

from typing import Any
from typing import Type

from src.banking_app.managers.base import BaseManager
from src.banking_app.models.client import Client


class ClientManager(BaseManager):
    @property
    def model(self) -> Type[Client]:
        return Client

    def bulk_create(
            self,
            session: Session,
            *,
            kwargs_list: list[dict[str, Any]],
    ) -> list[Client]:
        [kwargs.setdefault('status', 200) for kwargs in kwargs_list]
        return super().bulk_create(session, kwargs_list=kwargs_list)

    def create(self, session: Session, **kwargs) -> Client:
        kwargs.setdefault('status', 200)
        return super().create(session, **kwargs)

    def get_by_status(self, session: Session, *, status: int):
        query = (
            select(self.model)
            .join(self.model.client_status)
            .filter(self.model.status == status)
        )
        result = session.execute(query).scalars().all()
        return result
