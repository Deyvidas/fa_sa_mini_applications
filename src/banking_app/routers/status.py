from fastapi import APIRouter, Depends
from fastapi import status

from typing import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from src.banking_app.connection import activate_session
from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import Status
from src.banking_app.schemas.status import StatusCreate
from src.banking_app.schemas.status import StatusFullUpdate
from src.banking_app.schemas.status import StatusPartialUpdate
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.utils.exceptions import BaseExceptionRaiser
from src.banking_app.utils.exceptions import EmptyBodyOnPatchMessage
from src.banking_app.utils.exceptions import ErrorType
from src.banking_app.utils.exceptions import NotFoundMessage
from src.banking_app.utils.exceptions import UniquesViolationMessage


manager = StatusManager()
router = APIRouter(
    prefix='/status',
    tags=['Status description'],
)


@router.get(
    path='/list',
    status_code=status.HTTP_200_OK,
    response_model=list[StatusRetrieve],
)
def get_all_statuses(session: Session = Depends(activate_session)):
    statement = manager.filter()
    instances: Sequence[Status] = session.scalars(statement).unique().all()
    return [instance.to_dto_model(StatusRetrieve) for instance in instances]


@router.post(
    path='/list',
    status_code=status.HTTP_201_CREATED,
    response_model=list[StatusRetrieve],
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': UniquesViolationMessage}
    },
)
def add_statuses(
        statuses_data: list[StatusCreate],
        session: Session = Depends(activate_session),
):
    try:
        kwargs_list = [status.model_dump() for status in statuses_data]
        statement = manager.bulk_create(kwargs_list)
        instances: Sequence[Status] = session.scalars(statement).unique().all()
        session.commit()
        return [instance.to_dto_model(StatusRetrieve) for instance in instances]

    except IntegrityError as error:
        session.rollback()
        if 'status' not in error._message():
            raise
        BaseExceptionRaiser(
            model=Status,
            error_type=ErrorType.UNIQUE_VIOLATION_400,
            kwargs=manager.parse_integrity_error(error),
        ).raise_exception()


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=StatusRetrieve,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': UniquesViolationMessage},
    }
)
def add_status(
        status_data: StatusCreate,
        session: Session = Depends(activate_session),
):
    try:
        statement = manager.create(**status_data.model_dump())
        instance = session.scalar(statement)
        if isinstance(instance, Status):
            session.commit()
            return instance.to_dto_model(StatusRetrieve)

    except IntegrityError as error:
        session.rollback()
        if 'status' not in error._message():
            raise
        BaseExceptionRaiser(
            model=Status,
            error_type=ErrorType.UNIQUE_VIOLATION_400,
            kwargs=manager.parse_integrity_error(error),
        ).raise_exception()


@router.get(
    path='/{status_num}',
    status_code=status.HTTP_200_OK,
    response_model=StatusRetrieve,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def get_status_with_status_number(
        status_num: int,
        session: Session = Depends(activate_session),
):
    statement = manager.filter(status=status_num)
    instance = session.scalar(statement)
    if isinstance(instance, Status):
        return instance.to_dto_model(StatusRetrieve)

    BaseExceptionRaiser(
        model=Status,
        error_type=ErrorType.NOT_FOUND_404,
        kwargs=dict(status=status_num)
    ).raise_exception()


@router.put(
    path='/{status_num}',
    status_code=status.HTTP_200_OK,
    response_model=StatusRetrieve,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def full_update_status_with_status_number(
        status_num: int,
        new_data: StatusFullUpdate,
        session: Session = Depends(activate_session),
):
    statement = manager.update(
        where=dict(status=status_num),
        set_value=new_data.model_dump(),
    )
    instance = session.scalar(statement)
    if isinstance(instance, Status):
        session.commit()
        return instance.to_dto_model(StatusRetrieve)
    BaseExceptionRaiser(
        model=Status,
        error_type=ErrorType.NOT_FOUND_404,
        kwargs=dict(status=status_num),
    ).raise_exception()


@router.patch(
    path='/{status_num}',
    status_code=status.HTTP_200_OK,
    response_model=StatusRetrieve,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
        status.HTTP_400_BAD_REQUEST: {'model': EmptyBodyOnPatchMessage}
    },
)
def partial_update_status_with_status_number(
        status_num: int,
        new_data: StatusPartialUpdate,
        session: Session = Depends(activate_session),
):
    try:
        statement = manager.update(
            where=dict(status=status_num),
            set_value=new_data.model_dump(exclude_none=True),
        )
        instance = session.scalar(statement)
        if isinstance(instance, Status):
            session.commit()
            return instance.to_dto_model(StatusRetrieve)

        BaseExceptionRaiser(
            model=Status,
            error_type=ErrorType.NOT_FOUND_404,
            kwargs=dict(status=status_num),
        ).raise_exception()

    except ValueError as error:
        if not str(error).startswith('Without new values, updating can\'t proceed'):
            raise
        BaseExceptionRaiser(
            model=Status,
            error_type=ErrorType.EMPTY_BODY_ON_PATCH_400,
            kwargs=dict(status=status_num),
        ).raise_exception()


@router.delete(
    path='/{status_num}',
    status_code=status.HTTP_200_OK,
    response_model=StatusRetrieve,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def delete_status_with_status_number(
        status_num: int,
        session: Session = Depends(activate_session),
):
    statement = manager.delete(status=status_num)
    instance = session.scalar(statement)
    if isinstance(instance, Status):
        session.commit()
        return instance.to_dto_model(StatusRetrieve)

    BaseExceptionRaiser(
        model=Status,
        error_type=ErrorType.NOT_FOUND_404,
        kwargs=dict(status=status_num)
    ).raise_exception()
