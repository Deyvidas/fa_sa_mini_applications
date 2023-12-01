from fastapi import FastAPI

from src.banking_app.routers.status import router as router_status_description
from src.banking_app.routers.client import router as router_client


banking_app = FastAPI(title='Banking application')
banking_app.include_router(router_status_description)
banking_app.include_router(router_client)
