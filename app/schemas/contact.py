from pydantic import BaseModel, Field
from typing import Optional

class ContactBase(BaseModel):
    name: str = Field(..., example="Tharushi")
    email: str = Field(..., example="tharushi@gmail.com")
    phone: str = Field(..., example="0763334445")
    notes: Optional[str] = Field(None, example="Personal friend")

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class ContactResponse(ContactBase):
    id: str = Field(..., example="669c2f5b89a8f421b4a3901f")
    created_at: str
    is_valid: bool = True
