from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from pydantic import TypeAdapter

from sqlalchemy import select
from sqlalchemy.orm.session import Session

from typing import TypeAlias
from typing import Sequence

from src.banking_app.connection import activate_session
from src.banking_app.models.card import Card
from src.banking_app.schemas import CardDTO


router = APIRouter(
    prefix='/cards',
    tags=['Cards of client'],
)

RetrieveOneModel: TypeAlias = CardDTO
RetrieveManyModel: TypeAlias = Sequence[RetrieveOneModel]

RetrieveOne = TypeAdapter(RetrieveOneModel).validate_python
RetrieveMany = TypeAdapter(RetrieveManyModel).validate_python


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=RetrieveManyModel,
)
def get_cards(session: Session = Depends(activate_session)):
    query = select(Card)
    instances = session.execute(query).scalars().all()
    return RetrieveMany(instances)


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=RetrieveOneModel,
)
def add_card(
        card_data: CardDTO,
        session: Session = Depends(activate_session),
):
    instance = Card(**card_data.model_dump())
    session.add(instance)
    session.commit()
    return RetrieveOne(instance)
