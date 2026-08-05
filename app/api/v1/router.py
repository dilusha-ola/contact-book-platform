from fastapi import APIRouter, Depends
from app.api.v1 import contacts, companies
from app.core.security import verify_api_key

api_router = APIRouter(dependencies=[Depends(verify_api_key)])
api_router.include_router(contacts.router)
api_router.include_router(companies.router)
