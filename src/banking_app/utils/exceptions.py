from fastapi import HTTPException
from fastapi import status

from pydantic import BaseModel
from pydantic import Field

from typing import Any
from typing import NoReturn
from typing import Type

from src.banking_app.models.base import Base


class BaseErrorMessage(BaseModel):
    detail: str = Field(default='', examples=[''])


class UniquesViolationMessage(BaseModel):
    detail: str = Field(
        default='{model} which unique field value {kwargs} already exists',
        examples=[
            '{model} which unique field value {key}={value} already exists'
        ],
    )


class NotFoundMessage(BaseModel):
    detail: str = Field(
        default='{model} with {kwargs} not found.',
        examples=['{model} with {key1}={value1}, ...=... not found.'],
    )


class BaseExceptionRaiser(BaseModel):
    model: Type[Base]
    status: int
    kwargs: dict[str, Any]

    def raise_exception(self) -> NoReturn:
        status_exception = {
            status.HTTP_404_NOT_FOUND: self._raise_not_found,
            status.HTTP_400_BAD_REQUEST: self._raise_unique_violation,
        }
        status_exception.get(self.status)()

    def _raise_not_found(self) -> NoReturn:
        raise self._get_exception(message=self._message_not_found)

    def _raise_unique_violation(self) -> NoReturn:
        raise self._get_exception(message=self._message_unique_violation)

    def _get_exception(self, *, message: BaseErrorMessage):
        return HTTPException(status_code=self.status, detail=message)

    @property
    def _message_not_found(self) -> NotFoundMessage:
        return NotFoundMessage().detail.format(
            model=self._model,
            kwargs=self._kwargs,
        )

    @property
    def _message_unique_violation(self) -> UniquesViolationMessage:
        return UniquesViolationMessage().detail.format(
            model=self._model,
            kwargs=self._kwargs,
        )

    @property
    def _model(self) -> str:
        return self.model.__name__

    @property
    def _kwargs(self) -> str:
        return ', '.join([f'{k}={v}'for k, v in self.kwargs.items()])
