from fastapi import APIRouter
from fastapi import Depends

from http import HTTPStatus as status

from sqlalchemy import select
from sqlalchemy.orm.session import Session

from src.banking_app.connection import get_session
from src.banking_app.models.balance import Balance
from src.banking_app.schemas.balance import BalanceGetDTO
from src.banking_app.schemas.balance import BalancePostDTO


router = APIRouter(
    prefix='/balance',
    tags=['Balance'],
)


@router.get(
    path='/',
    status_code=status.OK,
    response_model=list[BalanceGetDTO],
)
def get_balances(session: Session = Depends(get_session)):
    query = select(Balance)
    instances = session.execute(query).scalars().all()
    result = [instance.to_dto_model(BalanceGetDTO) for instance in instances]
    return result


@router.post(
    path='/',
    status_code=status.CREATED,
    response_model=BalanceGetDTO,
)
def add_balance(
        balance_data: BalancePostDTO,
        session: Session = Depends(get_session),
):
    instance = Balance(**balance_data.model_dump())
    session.add(instance)
    session.commit()
    print(instance.client.full_name)
    return instance.to_dto_model(BalanceGetDTO)
