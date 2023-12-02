from fastapi import APIRouter
from fastapi import Depends

from http import HTTPStatus as status

from sqlalchemy import select
from sqlalchemy.orm.session import Session

from src.banking_app.connection import get_session
from src.banking_app.models.card import Card
from src.banking_app.schemas.card import CardDTO


router = APIRouter(
    prefix='/cards',
    tags=['Cards of client'],
)


@router.get(
    path='/',
    status_code=status.OK,
    response_model=list[CardDTO],
)
def get_cards(session: Session = Depends(get_session)):
    query = select(Card)
    instances = session.execute(query).scalars().all()
    for instance in instances:
        print(instance.client.full_name)
    result = [instance.to_dto_model(CardDTO) for instance in instances]
    return result


@router.post(
    path='/',
    status_code=status.CREATED,
    response_model=CardDTO,
)
def add_card(
        card_data: CardDTO,
        session: Session = Depends(get_session),
):
    instance = Card(**card_data.model_dump())
    session.add(instance)
    session.commit()
    return instance.to_dto_model(CardDTO)
