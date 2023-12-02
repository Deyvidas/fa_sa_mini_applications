from fastapi import APIRouter
from fastapi import Depends

from http import HTTPStatus as status

from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select

from src.banking_app.connection import get_session
from src.banking_app.models.transaction import Transaction
from src.banking_app.schemas.transaction import TransactionGetDTO
from src.banking_app.schemas.transaction import TransactionPostDTO


router = APIRouter(
    prefix='/transactions',
    tags=['Card transactions'],
)


@router.get(
    path='/',
    status_code=status.OK,
    response_model=list[TransactionGetDTO],
)
def get_transactions(session: Session = Depends(get_session)):
    query = select(Transaction)
    instances = session.execute(query).scalars().all()
    result = [inst.to_dto_model(TransactionGetDTO) for inst in instances]
    return result


@router.post(
    path='/',
    status_code=status.CREATED,
    response_model=TransactionGetDTO,
)
def add_transaction(
        transaction_data: TransactionPostDTO,
        session: Session = Depends(get_session),
):
    instance = Transaction(**transaction_data.model_dump())
    session.add(instance)
    session.commit()
    return instance.to_dto_model(TransactionGetDTO)
