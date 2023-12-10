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
from src.banking_app.schemas.balance import BalanceCreate
from src.banking_app.schemas.balance import BalanceRetrieve
from src.banking_app.types.general import MoneyAmount
from src.banking_app.utils.exceptions import BaseExceptionRaiser
from src.banking_app.utils.exceptions import NotFoundMessage


manager = BalanceManager()
router = APIRouter(
    prefix='/balances',
    tags=['Balance'],
)


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


@router.get(
    path='/list-balances-between',
    status_code=status.HTTP_200_OK,
    response_model=list[BalanceRetrieve],
)
def get_balances_with_amount_between(
        min_amount: MoneyAmount,
        max_amount: MoneyAmount,
        session: Session = Depends(activate_session),
):
    statement = manager.filter(
        current_amount__between=(min_amount, max_amount)
    )
    instances: list[Balance] = session.scalars(statement).unique().all()
    return [instance.to_dto_model(BalanceRetrieve) for instance in instances]


@router.get(
    path='/list',
    status_code=status.HTTP_200_OK,
    response_model=list[BalanceRetrieve],
)
def get_all_balances(session: Session = Depends(activate_session)):
    statement = manager.filter()
    instances: list[Balance] = session.scalars(statement).unique().all()
    return [instance.to_dto_model(BalanceRetrieve) for instance in instances]


@router.post(
    path='/list',
    status_code=status.HTTP_201_CREATED,
    response_model=list[BalanceRetrieve],
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def add_list_of_balances(
        balances_list: list[BalanceCreate],
        session: Session = Depends(activate_session),
):
    list_kwargs = [balance.model_dump() for balance in balances_list]
    statement = manager.bulk_create(list_kwargs)
    try:
        balances: list[Balance] = session.scalars(statement).unique().all()
        clients = set(balance.client for balance in balances)
        [client.actualize_balance() for client in clients]
        session.commit()
        return [balance.to_dto_model(BalanceRetrieve) for balance in balances]
    except IntegrityError as error:
        session.rollback()
        if 'client_id' in error.orig.diag.message_detail:
            raise_client_not_found(error)
        else:
            raise


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=BalanceRetrieve,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': NotFoundMessage},
    },
)
def add_balance(
        balance_data: BalanceCreate,
        session: Session = Depends(activate_session),
):
    statement = manager.create(**balance_data.model_dump())
    try:
        instance: Balance = session.scalar(statement)
        instance.client.actualize_balance()
        session.commit()
        return instance.to_dto_model(BalanceRetrieve)
    except IntegrityError as error:
        session.rollback()
        if 'client_id' in error.orig.diag.message_detail:
            raise_client_not_found(error)
        else:
            raise
