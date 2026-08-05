from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.services.company_service import company_service

router = APIRouter(prefix="/companies", tags=["Company Contact APIs"])

@router.get("", response_model=List[CompanyResponse], summary="List / Search Company Contacts")
async def list_companies(
    name: Optional[str] = Query(None, description="Filter specifically by company name"),
    company_email: Optional[str] = Query(None, description="Filter specifically by company email"),
    location: Optional[str] = Query(None, description="Filter specifically by location"),
    query: Optional[str] = Query(None, description="General search across name, company_email, phone, or location")
):
    """List company contacts with filtering."""
    return await company_service.get_all_companies(
        name=name,
        company_email=company_email,
        location=location,
        query=query
    )

@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED, summary="Create Company Contact")
async def create_company(payload: CompanyCreate):
    """Create a new company contact entry."""
    return await company_service.create_company(payload.model_dump())

@router.get("/stats", summary="Get Company Stats")
async def get_stats():
    """Retrieve stats for companies."""
    return await company_service.get_stats()

@router.get("/{company_id}", response_model=CompanyResponse, summary="Get Company Contact Details")
async def get_company(company_id: str):
    """Get specific company details by ID."""
    company = await company_service.get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ID '{company_id}' not found")
    return company

@router.put("/{company_id}", response_model=CompanyResponse, summary="Update Company Contact")
async def update_company(company_id: str, payload: CompanyUpdate):
    """Update existing company contact details."""
    updated = await company_service.update_company(company_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Company with ID '{company_id}' not found")
    return updated

@router.delete("/{company_id}", status_code=status.HTTP_200_OK, summary="Delete Company Contact")
async def delete_company(company_id: str):
    """Delete a company contact."""
    success = await company_service.delete_company(company_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Company with ID '{company_id}' not found")
    return {"message": f"Company '{company_id}' successfully deleted"}
