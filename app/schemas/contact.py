from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class ContactBase(BaseModel):
    name: str = Field(..., example="Nimal Perera")
    email: str = Field(..., example="nimal@gmail.com")
    phone: str = Field(..., example="0754578973")
    company: Optional[str] = Field(None, example="decryptogen")
    category: str = Field("Work", example="Work") # "Work", "Personal"
    notes: Optional[str] = Field(None, example="Software Engineer")

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
