from abc import ABC
from abc import abstractmethod

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.session import Session


class AbstractManager(ABC):

    @property
    @abstractmethod
    def model(self) -> DeclarativeBase: ...

    @property
    @abstractmethod
    def session(self) -> Session: ...
