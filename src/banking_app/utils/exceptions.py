from enum import Enum

from fastapi import HTTPException
from fastapi import status

from pydantic import BaseModel
from pydantic import Field

from typing import Any
from typing import NamedTuple
from typing import NoReturn

from src.banking_app.models.base import Base


class BaseErrorMessage(BaseModel):
    detail: str = Field(default='', examples=[''])


class NotFoundMessage(BaseErrorMessage):
    detail: str = Field(
        default='{model} with {kwargs} not found.',
        examples=['{model} with {key1}={value1}, ...=... not found.'],
    )


class UniquesViolationMessage(BaseErrorMessage):
    detail: str = Field(
        default='{model} with {kwargs} already exists.',
        examples=[
            '{model} with {key}={value} already exists.'
        ],
    )


class EmptyBodyOnPatchMessage(BaseErrorMessage):
    detail: str = Field(
        default='{model} with {kwargs} can\'t be updated, received empty body, change at least value of one field.',  # noqa: E501
        examples=['{model} with {key1}={value1}, ...=... can\'t be updated, received empty body, change at least value of one field.']  # noqa: E501
    )


class ErrorTypeDetail(NamedTuple):
    status_code: int
    error_message: BaseErrorMessage


class ErrorType(Enum):
    NOT_FOUND_404 = ErrorTypeDetail(
        status_code=status.HTTP_404_NOT_FOUND,
        error_message=NotFoundMessage(),
    )
    UNIQUE_VIOLATION_400 = ErrorTypeDetail(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_message=UniquesViolationMessage(),
    )
    EMPTY_BODY_ON_PATCH_400 = ErrorTypeDetail(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_message=EmptyBodyOnPatchMessage(),
    )


class BaseExceptionRaiser(BaseModel):
    model: type[Base]
    error_type: ErrorType
    kwargs: dict[str, Any]

    def raise_exception(self) -> NoReturn:
        error_detail = self.error_type.value
        status_code = error_detail.status_code
        detail = error_detail.error_message.detail.format(
            model=self._model,
            kwargs=self._kwargs,
        )
        raise HTTPException(status_code=status_code, detail=detail)

    @property
    def _model(self) -> str:
        return self.model.__name__

    @property
    def _kwargs(self) -> str:
        return ', '.join([f'{k}={v}'for k, v in self.kwargs.items()])
