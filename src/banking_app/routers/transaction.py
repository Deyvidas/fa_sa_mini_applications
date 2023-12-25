from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from pydantic import TypeAdapter

from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import select

from typing import Sequence
from typing import TypeAlias

from src.banking_app.connection import activate_session
from src.banking_app.models.transaction import Transaction
from src.banking_app.schemas import TransactionCreate
from src.banking_app.schemas import TransactionRetrieve


router = APIRouter(
    prefix='/transactions',
    tags=['Card transactions'],
)

RetrieveOneModel: TypeAlias = TransactionRetrieve
RetrieveManyModel: TypeAlias = Sequence[RetrieveOneModel]

RetrieveOne = TypeAdapter(RetrieveOneModel).validate_python
RetrieveMany = TypeAdapter(RetrieveManyModel).validate_python


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveManyModel,
)
def get_transactions(session: Session = Depends(activate_session)):
    query = select(Transaction)
    instances = session.execute(query).scalars().all()
    return RetrieveMany(instances)


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=RetrieveOneModel,
)
def add_transaction(
        transaction_data: TransactionCreate,
        session: Session = Depends(activate_session),
):
    instance = Transaction(**transaction_data.model_dump())
    session.add(instance)
    session.commit()
    return RetrieveOne(instance)
