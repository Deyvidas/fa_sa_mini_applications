from fastapi import APIRouter, Depends
from fastapi import status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from src.banking_app.connection import activate_session
from src.banking_app.managers.status import StatusManager
from src.banking_app.models.status import StatusDesc
from src.banking_app.schemas.status import StatusDescDTO
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
    response_model=list[StatusDescDTO],
)
def get_all_statuses(session: Session = Depends(activate_session)):
    statement = manager.filter()
    instances: list[StatusDesc] = session.scalars(statement).unique().all()
    return [instance.to_dto_model(StatusDescDTO) for instance in instances]


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=StatusDescDTO,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': UniquesViolationMessage},
    }
)
def add_status(
        status_data: StatusDescDTO,
        session: Session = Depends(activate_session),
):
    statement = manager.create(**status_data.model_dump())
    try:
        instance = session.scalar(statement)
        session.commit()
        return instance.to_dto_model(StatusDescDTO)
    except IntegrityError:
        BaseExceptionRaiser(
            model=StatusDesc,
            status=status.HTTP_400_BAD_REQUEST,
            kwargs=dict(status=status_data.status),
        ).raise_exception()


@router.get(
    path='/{status_num}',
    status_code=status.HTTP_200_OK,
    response_model=StatusDescDTO,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def get_status_with_status_number(
        status_num: int,
        session: Session = Depends(activate_session),
):
    statement = manager.filter(status=status_num)
    instance = session.scalars(statement).unique().all()

    if len(instance) == 1:
        return instance[0].to_dto_model(StatusDescDTO)
    BaseExceptionRaiser(
        model=StatusDesc,
        status=status.HTTP_404_NOT_FOUND,
        kwargs=dict(status=status_num)
    ).raise_exception()


@router.delete(
    path='/{status_num}',
    status_code=status.HTTP_200_OK,
    response_model=StatusDescDTO,
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
        return instance.to_dto_model(StatusDescDTO)
    BaseExceptionRaiser(
        model=StatusDesc,
        status=status.HTTP_404_NOT_FOUND,
        kwargs=dict(status=status_num)
    ).raise_exception()
