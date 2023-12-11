from fastapi import APIRouter, Depends
from fastapi import status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from src.banking_app.connection import activate_session
from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import Status
from src.banking_app.schemas.status import StatusCreate
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.schemas.status import StatusUpdate
from src.banking_app.utils.exceptions import BaseExceptionRaiser
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
    instances: list[Status] = session.scalars(statement).unique().all()
    return [instance.to_dto_model(StatusRetrieve) for instance in instances]


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
    statement = manager.create(**status_data.model_dump())
    try:
        instance: Status = session.scalar(statement)
        session.commit()
        return instance.to_dto_model(StatusRetrieve)
    except IntegrityError:
        BaseExceptionRaiser(
            model=Status,
            status=status.HTTP_400_BAD_REQUEST,
            kwargs=dict(status=status_data.status),
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
    instance: list[Status] = session.scalars(statement).unique().all()

    if len(instance) == 1:
        return instance[0].to_dto_model(StatusRetrieve)
    BaseExceptionRaiser(
        model=Status,
        status=status.HTTP_404_NOT_FOUND,
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
        new_data: StatusUpdate,
        session: Session = Depends(activate_session),
):
    statement = manager.update(
        where=dict(status=status_num),
        set_value=new_data.model_dump(),
    )
    instance: Status = session.scalar(statement)
    if instance is not None:
        session.commit()
        return instance.to_dto_model(StatusRetrieve)
    BaseExceptionRaiser(
        model=Status,
        status=status.HTTP_404_NOT_FOUND,
        kwargs=dict(status=status_num),
    ).raise_exception()


@router.patch(
    path='/{status_num}',
    status_code=status.HTTP_200_OK,
    response_model=StatusRetrieve,
)
def partial_update_status_with_status_number(
        status_num: int,
        new_data: StatusUpdate,
        session: Session = Depends(activate_session),
):
    ...


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
    session.commit()

    if instance is not None:
        return instance.to_dto_model(StatusRetrieve)
    BaseExceptionRaiser(
        model=Status,
        status=status.HTTP_404_NOT_FOUND,
        kwargs=dict(status=status_num)
    ).raise_exception()
