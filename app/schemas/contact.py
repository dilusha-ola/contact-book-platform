from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class ContactBase(BaseModel):
    name: str = Field(..., example="Sarah Connor")
    email: str = Field(..., example="sarah@cyberdyne.io")
    phone: str = Field(..., example="+1-800-555-0144")
    company: Optional[str] = Field(None, example="Cyberdyne Systems")
    category: str = Field("Work", example="Work") # "Work", "Personal"
    notes: Optional[str] = Field(None, example="Security lead")

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None

class ContactResponse(ContactBase):
    id: str = Field(..., example="669c2f5b89a8f421b4a3901f")
    created_at: str
    is_valid: bool = True
