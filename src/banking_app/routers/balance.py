import re

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from typing import NoReturn

from src.banking_app.connection import activate_session
from src.banking_app.managers.balance import BalanceManager
from src.banking_app.models.balance import Balance
from src.banking_app.models.client import Client
from src.banking_app.schemas.balance import BalanceGetDTO
from src.banking_app.schemas.balance import BalancePostDTO
from src.banking_app.schemas.client import ClientGetDTO
from src.banking_app.schemas.status import StatusDescDTO
from src.banking_app.types.general import MoneyAmount
from src.banking_app.utils.exceptions import BaseExceptionRaiser
from src.banking_app.utils.exceptions import NotFoundMessage


manager = BalanceManager()
router = APIRouter(
    prefix='/balances',
    tags=['Balance'],
)


def update_client_balance_flag(instance: Client) -> None:
    """
    Leave Balance.actual_flag=True for most recently Client.balances instance.
    """
    # WHERE Balance.actual_flag = true;
    actual_balances: list[Balance] = list(filter(
        lambda balance: balance.actual_flag is True, instance.balances
    ))
    if len(actual_balances) == 1:
        return
    # ORDER BY Balance.processed_datetime ASC;
    actual_balances = sorted(
        actual_balances,
        key=lambda balance: balance.processed_datetime,
    )
    # SET Balance.actual_flag = false;
    last_added_balance = actual_balances[-1]
    for balance in actual_balances:
        if balance == last_added_balance or balance.actual_flag is False:
            continue
        setattr(balance, 'actual_flag', False)


def raise_client_not_found(error: IntegrityError) -> NoReturn:
    """Parse IntegrityError message and raise exception."""
    error_message = error.orig.diag.message_detail
    key_value_regex = r'\(client_id\)=\([\d]+\)'
    parenthesis_regex = r'[\(\)]'

    key_value = re.findall(key_value_regex, error_message)[0]
    key_value = re.sub(parenthesis_regex, '', key_value)

    BaseExceptionRaiser(
        model=Client,
        status=status.HTTP_404_NOT_FOUND,
        kwargs=eval(f'dict({key_value})')
    ).raise_exception()


def get_balance_dto_model(instance: Balance) -> BalanceGetDTO:
    balance_model = instance.to_dto_model(BalanceGetDTO)
    client_model = balance_model.client.to_dto_model(ClientGetDTO)
    status_model = balance_model.client.client_status.to_dto_model(StatusDescDTO)  # noqa: E501

    balance_model.client = client_model
    balance_model.client.status = status_model
    return balance_model


@router.get(
    path='/list-with-balances-between',
    status_code=status.HTTP_200_OK,
    response_model=list[BalanceGetDTO],
)
def get_balances_with_amount_between(
        min_amount: MoneyAmount,
        max_amount: MoneyAmount,
        session: Session = Depends(activate_session),
):
    statement = manager.filter(
        current_amount__between=(min_amount, max_amount)
    )
    instances = session.scalars(statement).all()
    return [get_balance_dto_model(instance) for instance in instances]


@router.get(
    path='/list',
    status_code=status.HTTP_200_OK,
    response_model=list[BalanceGetDTO],
)
def get_all_balances(session: Session = Depends(activate_session)):
    statement = manager.filter()
    instances = session.scalars(statement).all()
    return [get_balance_dto_model(instance) for instance in instances]


@router.post(
    path='/list',
    status_code=status.HTTP_201_CREATED,
    response_model=list[BalanceGetDTO],
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def add_list_of_balances(
        balances_list: list[BalancePostDTO],
        session: Session = Depends(activate_session),
):
    list_kwargs = [balance.model_dump() for balance in balances_list]
    statement = manager.bulk_create(list_kwargs)
    try:
        instances: list[Balance] = session.scalars(statement).all()
        clients = set(instance.client for instance in instances)
        [update_client_balance_flag(client) for client in clients]
        # session.commit()
        return [get_balance_dto_model(instance) for instance in instances]
    except IntegrityError as error:
        session.rollback()
        if 'client_id' in error.orig.diag.message_detail:
            raise_client_not_found(error)
        else:
            raise


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=BalanceGetDTO,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def add_balance(
        balance_data: BalancePostDTO,
        session: Session = Depends(activate_session),
):
    statement = manager.create(**balance_data.model_dump())
    try:
        instance: Balance = session.execute(statement).scalar()
        update_client_balance_flag(instance.client)
        # session.commit()
        return get_balance_dto_model(instance)
    except IntegrityError as error:
        session.rollback()
        if 'client_id' in error.orig.diag.message_detail:
            raise_client_not_found(error)
        else:
            raise
