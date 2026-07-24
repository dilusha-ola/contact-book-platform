from typing import Optional
from app.repositories.company_repo import company_repo

class CompanyService:
    async def get_all_companies(
        self,
        name: Optional[str] = None,
        company_email: Optional[str] = None,
        location: Optional[str] = None,
        query: Optional[str] = None
    ):
        return await company_repo.get_all(
            name=name,
            company_email=company_email,
            location=location,
            query=query
        )

    async def get_company_by_id(self, company_id: str):
        return await company_repo.get_by_id(company_id)

    async def create_company(self, data: dict):
        return await company_repo.create(data)

    async def update_company(self, company_id: str, data: dict):
        return await company_repo.update(company_id, data)

    async def delete_company(self, company_id: str):
        return await company_repo.delete(company_id)

    async def get_stats(self):
        return await company_repo.get_stats()

company_service = CompanyService()
