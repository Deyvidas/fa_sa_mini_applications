from fastapi import APIRouter, Depends
from fastapi import status

from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from src.banking_app.connection import get_session
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
def get_statuses(session: Session = Depends(get_session)):
    instances = manager.filter(session)
    result = [instance.to_dto_model(StatusDescDTO) for instance in instances]
    return result


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
        session: Session = Depends(get_session),
):
    try:
        instance = manager.create(session, **status_data.model_dump())
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
def get_status_with_id(
        status_num: int,
        session: Session = Depends(get_session),
):
    try:
        instance = manager.get(session, status=status_num)
        return instance.to_dto_model(StatusDescDTO)
    except NoResultFound:
        BaseExceptionRaiser(
            model=StatusDesc,
            status=status.HTTP_404_NOT_FOUND,
            kwargs=dict(status=status_num)
        ).raise_exception()
