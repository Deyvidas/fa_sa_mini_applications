from fastapi import APIRouter
from fastapi import Depends

from http import HTTPStatus as status

from sqlalchemy import select
from sqlalchemy.orm.session import Session

from src.banking_app.connection import get_session
from src.banking_app.models.client import Client
from src.banking_app.schemas.client import ClientCreateDTO
from src.banking_app.schemas.client import ClientFetchDTO


router = APIRouter(
    prefix='/clients',
    tags=['Client'],
)


@router.get(
    path='/',
    status_code=status.OK,
    response_model=list[ClientFetchDTO],
)
def get_users(session: Session = Depends(get_session)):
    query = select(Client)
    instances = session.execute(query).scalars().all()
    result = [instance.to_dto_model(ClientFetchDTO) for instance in instances]
    return result


@router.post(
    path='/',
    status_code=status.CREATED,
    response_model=ClientFetchDTO,
)
def add_client(
        client_data: ClientCreateDTO,
        session: Session = Depends(get_session),
):
    instance = Client(**client_data.model_dump())
    session.add(instance)
    session.commit()
    return instance.to_dto_model(ClientFetchDTO)
