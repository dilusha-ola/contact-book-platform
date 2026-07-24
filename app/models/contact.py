from pydantic import BaseModel, Field
from typing import Optional

class ContactModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str = Field(..., description="Full name of personal contact")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    notes: Optional[str] = Field(None, description="Optional notes or remarks")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    is_valid: bool = Field(True, description="Email validity flag")

    class Config:
        populate_by_name = True
