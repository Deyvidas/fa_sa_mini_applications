from fastapi import FastAPI

from src.banking_app.routers.balance import router as router_balance
from src.banking_app.routers.card import router as router_card
from src.banking_app.routers.client import router as router_client
from src.banking_app.routers.status import router as router_status_description
from src.banking_app.routers.transaction import router as router_transaction


banking_app = FastAPI(title='Banking application')
banking_app.include_router(router_balance)
# banking_app.include_router(router_card)
banking_app.include_router(router_client)
# banking_app.include_router(router_status_description)
# banking_app.include_router(router_transaction)
