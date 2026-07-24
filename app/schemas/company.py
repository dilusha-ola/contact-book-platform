from pydantic import BaseModel, Field
from typing import List, Optional

class CompanyMember(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    phone: str

class CompanyResponse(BaseModel):
    company: str = Field(..., example="Decryptogen")
    contact_count: int = Field(..., example=3)
    members: List[CompanyMember] = []
