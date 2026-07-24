from typing import Optional
from app.repositories.contact_repo import contact_repo

class ContactService:
    async def get_all_contacts(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        query: Optional[str] = None
    ):
        return await contact_repo.get_all(
            name=name,
            email=email,
            query=query
        )

    async def get_contact_by_id(self, contact_id: str):
        return await contact_repo.get_by_id(contact_id)

    async def create_contact(self, data: dict):
        return await contact_repo.create(data)

    async def update_contact(self, contact_id: str, data: dict):
        return await contact_repo.update(contact_id, data)

    async def delete_contact(self, contact_id: str):
        return await contact_repo.delete(contact_id)

    async def get_stats(self):
        return await contact_repo.get_stats()

contact_service = ContactService()
