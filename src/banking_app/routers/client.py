from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from sqlalchemy.orm.session import Session

from src.banking_app.connection import get_session
from src.banking_app.managers.client import ClientManager
from src.banking_app.models.client import Client
from src.banking_app.schemas.client import ClientGetDTO
from src.banking_app.schemas.client import ClientPostDTO
from src.banking_app.schemas.status import StatusDescDTO


manager = ClientManager()
router = APIRouter(
    prefix='/clients',
    tags=['Client'],
)


def get_client_with_full_status(instance: Client):
    model = instance.to_dto_model(ClientGetDTO)
    model.status = instance.client_status.to_dto_model(StatusDescDTO)
    return model


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=list[ClientGetDTO],
)
def get_clients(session: Session = Depends(get_session)):
    instances = manager.filter(session)
    result = [instance.to_dto_model(ClientGetDTO) for instance in instances]
    return result


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=ClientGetDTO,
)
def add_client(
        client_data: ClientPostDTO,
        session: Session = Depends(get_session),
):
    instance = manager.create(session, **client_data.model_dump())
    return instance.to_dto_model(ClientGetDTO)


@router.post(
    path='/list',
    status_code=status.HTTP_201_CREATED,
    response_model=list[ClientGetDTO],
)
def add_clients(
        clients_list: list[ClientPostDTO],
        session: Session = Depends(get_session),
):
    kwargs_list = [data.model_dump() for data in clients_list]
    instances = manager.bulk_create(session, kwargs_list=kwargs_list)
    return [get_client_with_full_status(instance) for instance in instances]


@router.get(
    path='/list/{status_code}',
    status_code=status.HTTP_200_OK,
    response_model=list[ClientGetDTO],
)
def get_all_clients_with_status(
        status_code: int,
        session: Session = Depends(get_session),
):
    instances = manager.get_by_status(session, status=status_code)
    return [get_client_with_full_status(instance) for instance in instances]
