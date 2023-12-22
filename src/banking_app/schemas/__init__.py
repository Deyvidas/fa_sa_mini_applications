from src.banking_app.schemas.base import Base

from src.banking_app.schemas.balance import BalanceCreate
from src.banking_app.schemas.balance import BalanceRetrieve

from src.banking_app.schemas.card import CardDTO

from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.schemas.client import ClientModelWithRelations
from src.banking_app.schemas.client import ClientCreate
from src.banking_app.schemas.client import ClientFullUpdate
from src.banking_app.schemas.client import ClientPartialUpdate
from src.banking_app.schemas.client import ClientRetrieve

from src.banking_app.schemas.status import BaseStatusModel
from src.banking_app.schemas.status import StatusModelWithRelations
from src.banking_app.schemas.status import StatusCreate
from src.banking_app.schemas.status import StatusFullUpdate
from src.banking_app.schemas.status import StatusPartialUpdate
from src.banking_app.schemas.status import StatusRetrieve

from src.banking_app.schemas.transaction import TransactionGetDTO
from src.banking_app.schemas.transaction import TransactionPostDTO


BalanceCreate.model_rebuild()
BalanceRetrieve.model_rebuild()

CardDTO.model_rebuild()

BaseClientModel.model_rebuild()
ClientModelWithRelations.model_rebuild()
ClientCreate.model_rebuild()
ClientFullUpdate.model_rebuild()
ClientPartialUpdate.model_rebuild()
ClientRetrieve.model_rebuild()

BaseStatusModel.model_rebuild()
StatusModelWithRelations.model_rebuild()
StatusCreate.model_rebuild()
StatusFullUpdate.model_rebuild()
StatusPartialUpdate.model_rebuild()
StatusRetrieve.model_rebuild()

TransactionGetDTO.model_rebuild()
TransactionPostDTO.model_rebuild()


__all__ = (
    'BalanceCreate',
    'BalanceRetrieve',

    'Base',

    'CardDTO',

    'BaseClientModel',
    'ClientModelWithRelations',
    'ClientCreate',
    'ClientFullUpdate',
    'ClientPartialUpdate',
    'ClientRetrieve',

    'BaseStatusModel',
    'StatusModelWithRelations',
    'StatusCreate',
    'StatusFullUpdate',
    'StatusPartialUpdate',
    'StatusRetrieve',

    'TransactionGetDTO',
    'TransactionPostDTO',
)
