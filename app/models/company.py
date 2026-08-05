from pydantic import BaseModel, Field
from typing import Optional

class CompanyModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str = Field(..., description="Company name")
    company_email: str = Field(..., description="Official company email address")
    phone: str = Field(..., description="Company phone number")
    location: str = Field(..., description="Company physical location/address")
    notes: Optional[str] = Field(None, description="Optional notes or remarks")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    is_valid: bool = Field(True, description="Company email validity flag")

    class Config:
        populate_by_name = True
