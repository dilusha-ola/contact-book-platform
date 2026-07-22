from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.services.contact_service import contact_service

router = APIRouter(prefix="/contacts", tags=["Contact CRUD APIs"])

@router.get("", response_model=List[ContactResponse], summary="List / Filter Contacts")
async def list_contacts(
    name: Optional[str] = Query(None, description="Filter specifically by name (e.g. Nimal)"),
    email: Optional[str] = Query(None, description="Filter specifically by email (e.g. nimal@gmail.com)"),
    company: Optional[str] = Query(None, description="Filter specifically by company (e.g. decryptogen)"),
    category: Optional[str] = Query(None, description="Filter by category ('Work', 'Personal')"),
    query: Optional[str] = Query(None, description="General search across name, email, or company")
):
    """List contacts with multi-parameter filtering (e.g. ?name=Nimal&email=nimal@gmail.com)."""
    return await contact_service.get_all_contacts(
        name=name,
        email=email,
        company=company,
        category=category,
        query=query
    )

@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, summary="Create Contact")
async def create_contact(payload: ContactCreate):
    """Create a new contact entry in MongoDB Atlas."""
    return await contact_service.create_contact(payload.model_dump())

@router.get("/stats", summary="Get Platform Stats")
async def get_stats():
    """Retrieve platform analytics stats for Dashboard view."""
    return await contact_service.get_stats()

@router.get("/{contact_id}", response_model=ContactResponse, summary="Get Contact Details")
async def get_contact(contact_id: str):
    """Get specific contact details by MongoDB ObjectId."""
    contact = await contact_service.get_contact_by_id(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact with ID '{contact_id}' not found")
    return contact

@router.put("/{contact_id}", response_model=ContactResponse, summary="Update Contact")
async def update_contact(contact_id: str, payload: ContactUpdate):
    """Update existing contact details in MongoDB."""
    updated = await contact_service.update_contact(contact_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Contact with ID '{contact_id}' not found")
    return updated

@router.delete("/{contact_id}", status_code=status.HTTP_200_OK, summary="Delete Contact")
async def delete_contact(contact_id: str):
    """Delete a contact from MongoDB database."""
    success = await contact_service.delete_contact(contact_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Contact with ID '{contact_id}' not found")
    return {"message": f"Contact '{contact_id}' successfully deleted"}
