from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from sqlalchemy.orm.session import Session

from src.banking_app.conf import NotSpecifiedParam
from src.banking_app.connection import activate_session
from src.banking_app.managers.client import ClientManager
from src.banking_app.models.client import Client
from src.banking_app.schemas.client import ClientGetDTO
from src.banking_app.schemas.client import ClientPostDTO
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.types.client import Sex
from src.banking_app.utils.exceptions import BaseExceptionRaiser
from src.banking_app.utils.exceptions import NotFoundMessage


manager = ClientManager()
router = APIRouter(
    prefix='/clients',
    tags=['Client'],
)


def get_client_with_full_status(instance: Client):
    model = instance.to_dto_model(ClientGetDTO)
    model.status = instance.client_status.to_dto_model(StatusRetrieve)
    return model


@router.get(
    path='/list-filtered',
    status_code=status.HTTP_200_OK,
    response_model=list[ClientGetDTO],
)
def get_clients_filtered_by(
        status_code: int = NotSpecifiedParam,
        phone_number: str = NotSpecifiedParam,
        has_vip_status: bool = NotSpecifiedParam,
        sex: Sex = NotSpecifiedParam,
        session: Session = Depends(activate_session),
):
    statement = manager.filter(
        status=status_code,
        phone=phone_number,
        VIP_flag=has_vip_status,
        sex=sex,
    )
    instances = session.scalars(statement).unique().all()
    return [get_client_with_full_status(instance) for instance in instances]


@router.get(
    path='/list',
    status_code=status.HTTP_200_OK,
    response_model=list[ClientGetDTO],
)
def get_all_clients(session: Session = Depends(activate_session)):
    statement = manager.filter()
    instances = session.scalars(statement).unique().all()
    return [get_client_with_full_status(instance) for instance in instances]


@router.post(
    path='/list',
    status_code=status.HTTP_201_CREATED,
    response_model=list[ClientGetDTO],
)
def add_list_of_clients(
        clients_list: list[ClientPostDTO],
        session: Session = Depends(activate_session),
):
    list_kwargs = [data.model_dump() for data in clients_list]
    statement = manager.bulk_create(list_kwargs)
    instances = session.scalars(statement).unique().all()
    session.commit()
    return [get_client_with_full_status(instance) for instance in instances]


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=ClientGetDTO,
)
def add_client(
        client_data: ClientPostDTO,
        session: Session = Depends(activate_session),
):
    statement = manager.create(**client_data.model_dump())
    instance: Client = session.scalar(statement)
    session.commit()
    return get_client_with_full_status(instance)


@router.get(
    path='/{client_id}',
    status_code=status.HTTP_200_OK,
    response_model=ClientGetDTO,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def get_client_by_id(
        client_id: int,
        session: Session = Depends(activate_session),
):
    statement = manager.filter(client_id=client_id)
    instance = session.scalars(statement).unique().all()
    if len(instance) == 1:
        return get_client_with_full_status(instance[0])
    BaseExceptionRaiser(
        model=Client,
        status=status.HTTP_404_NOT_FOUND,
        kwargs=dict(client_id=client_id),
    ).raise_exception()


@router.delete(
    path='/{client_id}',
    status_code=status.HTTP_200_OK,
    response_model=ClientGetDTO,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def delete_client_with_id(
        client_id: int,
        session: Session = Depends(activate_session),
):
    statement = manager.delete(client_id=client_id)
    instance = session.scalar(statement)
    session.commit()

    if instance is not None:
        return get_client_with_full_status(instance)
    BaseExceptionRaiser(
        model=Client,
        status=status.HTTP_404_NOT_FOUND,
        kwargs=dict(client_id=client_id),
    ).raise_exception()
