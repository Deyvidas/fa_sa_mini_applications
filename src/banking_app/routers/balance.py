from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from pydantic import TypeAdapter

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from typing import TypeAlias
from typing import Sequence

from src.banking_app.connection import activate_session
from src.banking_app.managers.balance import BalanceManager
from src.banking_app.models.balance import Balance
from src.banking_app.schemas import BalanceCreate
from src.banking_app.schemas import BalanceRetrieve
from src.banking_app.types.general import MoneyAmount
from src.banking_app.utils.exceptions import BaseExceptionRaiser
from src.banking_app.utils.exceptions import ErrorType
from src.banking_app.utils.exceptions import NotFoundMessage


manager = BalanceManager()
router = APIRouter(
    prefix='/balances',
    tags=['Balance'],
)

RetrieveOneModel: TypeAlias = BalanceRetrieve
RetrieveManyModel: TypeAlias = Sequence[RetrieveOneModel]

RetrieveOne = TypeAdapter(RetrieveOneModel).validate_python
RetrieveMany = TypeAdapter(RetrieveManyModel).validate_python


@router.get(
    path='/list-balances-between',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveManyModel,
)
def get_balances_with_amount_between(
        min_amount: MoneyAmount,
        max_amount: MoneyAmount,
        session: Session = Depends(activate_session),
):
    statement = manager.filter(
        current_amount__between=(min_amount, max_amount)
    )
    instances: Sequence[Balance] = session.scalars(statement).unique().all()
    return RetrieveMany(instances)


@router.get(
    path='/list',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveManyModel,
)
def get_all_balances(session: Session = Depends(activate_session)):
    statement = manager.filter()
    instances: Sequence[Balance] = session.scalars(statement).unique().all()
    return RetrieveMany(instances)


@router.post(
    path='/list',
    status_code=status.HTTP_201_CREATED,
    response_model=RetrieveManyModel,
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
        balances: Sequence[Balance] = session.scalars(statement).unique().all()
        clients = set(balance.client for balance in balances)
        [client.actualize_balance() for client in clients]
        session.commit()
        return RetrieveMany(balances)
    except IntegrityError as error:
        session.rollback()
        if 'client_id' not in error._message():
            raise
        kwargs = manager.parse_integrity_error(error)
        BaseExceptionRaiser(
            model=Balance,
            error_type=ErrorType.UNIQUE_VIOLATION_400,
            kwargs=kwargs,
        ).raise_exception()


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=RetrieveOneModel,
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
        return RetrieveOne(instance)
    except IntegrityError as error:
        session.rollback()
        if 'client_id' not in error._message():
            raise
        kwargs = manager.parse_integrity_error(error)
        BaseExceptionRaiser(
            model=Balance,
            error_type=ErrorType.UNIQUE_VIOLATION_400,
            kwargs=kwargs,
        ).raise_exception()
