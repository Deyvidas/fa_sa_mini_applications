from src.banking_app.types.general import BaseEnum


class CardType(str, BaseEnum):
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'
