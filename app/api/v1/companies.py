from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.company import CompanyResponse
from app.services.contact_service import contact_service

router = APIRouter(prefix="/companies", tags=["Company APIs"])

@router.get("", response_model=List[CompanyResponse], summary="Get All Companies")
async def list_companies():
    """Retrieve list of unique companies registered in the Contact Book Platform with member details."""
    return await contact_service.get_companies()
