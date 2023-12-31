from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from pydantic import TypeAdapter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from typing import Sequence
from typing import TypeAlias

from src.banking_app.conf import NotSpecifiedParam
from src.banking_app.connection import activate_session
from src.banking_app.managers.client import ClientManager
from src.banking_app.models.client import Client
from src.banking_app.models.status import Status
from src.banking_app.schemas import ClientCreate
from src.banking_app.schemas import ClientFullUpdate
from src.banking_app.schemas import ClientPartialUpdate
from src.banking_app.schemas import ClientRetrieve
from src.banking_app.types.client import SexEnum
from src.banking_app.utils.exceptions import BaseExceptionRaiser
from src.banking_app.utils.exceptions import EmptyBodyOnPatchMessage
from src.banking_app.utils.exceptions import ErrorType
from src.banking_app.utils.exceptions import NotFoundMessage


manager = ClientManager()
router = APIRouter(
    prefix='/clients',
    tags=['Client'],
)

RetrieveOneModel: TypeAlias = ClientRetrieve
RetrieveManyModel: TypeAlias = Sequence[RetrieveOneModel]

RetrieveOne = TypeAdapter(RetrieveOneModel).validate_python
RetrieveMany = TypeAdapter(RetrieveManyModel).validate_python


@router.get(
    path='/list-filtered',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveManyModel,
)
def get_clients_filtered_by(
        status_code: int = NotSpecifiedParam,                                   # type: ignore
        phone_number: str = NotSpecifiedParam,                                  # type: ignore
        has_vip_status: bool = NotSpecifiedParam,                               # type: ignore
        sex: SexEnum = NotSpecifiedParam,                                       # type: ignore
        session: Session = Depends(activate_session),
):
    statement = manager.filter(
        status=status_code,
        phone=phone_number,
        VIP_flag=has_vip_status,
        sex=sex,
    )
    instances: Sequence[Client] = session.scalars(statement).unique().all()
    return RetrieveMany(instances)


@router.get(
    path='/list',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveManyModel,
)
def get_all_clients(session: Session = Depends(activate_session)):
    statement = manager.filter()
    instances: Sequence[Client] = session.scalars(statement).unique().all()
    return RetrieveMany(instances)


@router.post(
    path='/list',
    status_code=status.HTTP_201_CREATED,
    response_model=RetrieveManyModel,
)
def add_clients(
        clients_list: list[ClientCreate],
        session: Session = Depends(activate_session),
):
    list_kwargs = [data.model_dump() for data in clients_list]
    statement = manager.bulk_create(list_kwargs)
    instances: Sequence[Client] = session.scalars(statement).unique().all()
    session.commit()
    return RetrieveMany(instances)


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=RetrieveOneModel,
)
def add_client(
        client_data: ClientCreate,
        session: Session = Depends(activate_session),
):
    statement = manager.create(**client_data.model_dump())
    instance = session.scalar(statement)
    if isinstance(instance, Client):
        session.commit()
        return RetrieveOne(instance)
    raise ValueError(
        f'Something went wrong when try post to\n'
        f' url={router.prefix}\n'
        f'data={client_data.model_dump()}'
    )


@router.get(
    path='/{client_id}',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveOneModel,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def get_client_with_client_id(
        client_id: int,
        session: Session = Depends(activate_session),
):
    statement = manager.filter(client_id=client_id)
    instance = session.scalar(statement)
    if isinstance(instance, Client):
        return RetrieveOne(instance)
    BaseExceptionRaiser(
        model=Client,
        error_type=ErrorType.NOT_FOUND_404,
        kwargs=dict(client_id=client_id),
    ).raise_exception()


@router.put(
    path='/{client_id}',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveOneModel,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def full_update_client_with_client_id(
    client_id: int,
    client_data: ClientFullUpdate,
    session: Session = Depends(activate_session),
):
    statement = manager.update(
        where=dict(client_id=client_id),
        set_value=client_data.model_dump(),
    )
    try:
        instance = session.scalar(statement)

    except IntegrityError as error:
        if 'status' not in error._message():
            raise
        BaseExceptionRaiser(
            model=Status,
            error_type=ErrorType.NOT_FOUND_404,
            kwargs=manager.parse_integrity_error(error),
        ).raise_exception()

    if isinstance(instance, Client):
        session.commit()
        session.refresh(instance)
        return RetrieveOne(instance)
    BaseExceptionRaiser(
        model=Client,
        error_type=ErrorType.NOT_FOUND_404,
        kwargs=dict(client_id=client_id),
    ).raise_exception()


@router.patch(
    path='/{client_id}',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveOneModel,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
        status.HTTP_400_BAD_REQUEST: {'model': EmptyBodyOnPatchMessage}
    },
)
def partial_update_client_with_client_id(
    client_id: int,
    client_data: ClientPartialUpdate,
    session: Session = Depends(activate_session),
):
    where_kwargs = dict(client_id=client_id)

    try:
        statement = manager.update(
            where=where_kwargs,
            set_value=client_data.model_dump(exclude_none=True)
        )
        try:
            instance = session.scalar(statement)

        except IntegrityError as error:
            if 'status' not in error._message():
                raise
            BaseExceptionRaiser(
                model=Status,
                error_type=ErrorType.NOT_FOUND_404,
                kwargs=manager.parse_integrity_error(error),
            ).raise_exception()

        if isinstance(instance, Client):
            session.commit()
            return RetrieveOne(instance)

        BaseExceptionRaiser(
            model=Client,
            error_type=ErrorType.NOT_FOUND_404,
            kwargs=where_kwargs,
        ).raise_exception()

    except ValueError as error:
        if not str(error).startswith('Without new values, updating can\'t proceed'):
            raise
        BaseExceptionRaiser(
            model=Client,
            error_type=ErrorType.EMPTY_BODY_ON_PATCH_400,
            kwargs=where_kwargs,
        ).raise_exception()


@router.delete(
    path='/{client_id}',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveOneModel,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def delete_client_with_client_id(
        client_id: int,
        session: Session = Depends(activate_session),
):
    statement = manager.delete(client_id=client_id)
    instance = session.scalar(statement)
    session.commit()

    if isinstance(instance, Client):
        return RetrieveOne(instance)
    BaseExceptionRaiser(
        model=Client,
        error_type=ErrorType.NOT_FOUND_404,
        kwargs=dict(client_id=client_id),
    ).raise_exception()
