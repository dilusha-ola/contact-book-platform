from fastapi import APIRouter
from app.api.v1 import contacts, companies

api_router = APIRouter()
api_router.include_router(contacts.router)
api_router.include_router(companies.router)

