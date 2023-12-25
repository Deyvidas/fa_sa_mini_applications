from src.banking_app.schemas.base import Base

from src.banking_app.schemas.balance import BaseBalanceModel
from src.banking_app.schemas.balance import BalanceModelWithRelations
from src.banking_app.schemas.balance import BalanceRetrieve
from src.banking_app.schemas.balance import BalanceCreate

from src.banking_app.schemas.card import BaseCardModel
from src.banking_app.schemas.card import CardModelWithRelations
from src.banking_app.schemas.card import CardRetrieve
from src.banking_app.schemas.card import CardCreate

from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.schemas.client import ClientModelWithRelations
from src.banking_app.schemas.client import ClientRetrieve
from src.banking_app.schemas.client import ClientCreate
from src.banking_app.schemas.client import ClientFullUpdate
from src.banking_app.schemas.client import ClientPartialUpdate

from src.banking_app.schemas.status import BaseStatusModel
from src.banking_app.schemas.status import StatusModelWithRelations
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.schemas.status import StatusCreate
from src.banking_app.schemas.status import StatusFullUpdate
from src.banking_app.schemas.status import StatusPartialUpdate

from src.banking_app.schemas.transaction import BaseTransactionModel
from src.banking_app.schemas.transaction import TransactionModelWithRelations
from src.banking_app.schemas.transaction import TransactionRetrieve
from src.banking_app.schemas.transaction import TransactionCreate


BaseBalanceModel.model_rebuild()
BalanceModelWithRelations.model_rebuild()
BalanceRetrieve.model_rebuild()
BalanceCreate.model_rebuild()

BaseCardModel.model_rebuild()
CardModelWithRelations.model_rebuild()
CardRetrieve.model_rebuild()
CardCreate.model_rebuild()

BaseClientModel.model_rebuild()
ClientModelWithRelations.model_rebuild()
ClientRetrieve.model_rebuild()
ClientCreate.model_rebuild()
ClientFullUpdate.model_rebuild()
ClientPartialUpdate.model_rebuild()

BaseStatusModel.model_rebuild()
StatusModelWithRelations.model_rebuild()
StatusRetrieve.model_rebuild()
StatusCreate.model_rebuild()
StatusFullUpdate.model_rebuild()
StatusPartialUpdate.model_rebuild()

BaseTransactionModel.model_rebuild()
TransactionModelWithRelations.model_rebuild()
TransactionRetrieve.model_rebuild()
TransactionCreate.model_rebuild()


__all__ = (
    'Base',

    'BaseBalanceModel',
    'BalanceModelWithRelations',
    'BalanceRetrieve',
    'BalanceCreate',

    'BaseCardModel',
    'CardModelWithRelations',
    'CardRetrieve',
    'CardCreate',

    'BaseClientModel',
    'ClientModelWithRelations',
    'ClientRetrieve',
    'ClientCreate',
    'ClientFullUpdate',
    'ClientPartialUpdate',

    'BaseStatusModel',
    'StatusModelWithRelations',
    'StatusRetrieve',
    'StatusCreate',
    'StatusFullUpdate',
    'StatusPartialUpdate',

    'BaseTransactionModel',
    'TransactionModelWithRelations',
    'TransactionRetrieve',
    'TransactionCreate',
)
