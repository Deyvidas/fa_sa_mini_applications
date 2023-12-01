from fastapi import APIRouter
from fastapi import Depends

from http import HTTPStatus as status

from sqlalchemy import select
from sqlalchemy.orm.session import Session

from src.banking_app.connection import get_session
from src.banking_app.models.status import StatusDesc
from src.banking_app.schemas.status import StatusDescDTO


router = APIRouter(
    prefix='/status',
    tags=['Status description'],
)


@router.get(
        path='/',
        status_code=status.OK,
        response_model=list[StatusDescDTO],
)
def get_statuses(session: Session = Depends(get_session)):
    query = select(StatusDesc)
    instances = session.execute(query).scalars().all()
    result = [instance.to_dto_model(StatusDescDTO) for instance in instances]
    return result


@router.post(
        path='/',
        status_code=status.CREATED,
        response_model=StatusDescDTO,
)
def add_status(
        status_data: StatusDescDTO,
        session: Session = Depends(get_session),
):
    instance = StatusDesc(**status_data.model_dump())
    session.add(instance)
    session.commit()
    return instance.to_dto_model(StatusDescDTO)
