from pydantic import BaseModel, Field
from typing import Optional, List

class CompanyBase(BaseModel):
    name: str = Field(..., example="Decryptogen")
    company_email: str = Field(..., example="info@decryptogen.com")
    phone: str = Field(..., example="0112345678")
    location: str = Field(..., example="Colombo, Sri Lanka")
    notes: Optional[str] = Field(None, example="Software Engineering Services")

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    company_email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: str = Field(..., example="669c2f5b89a8f421b4a3901f")
    created_at: str
    is_valid: bool = True
