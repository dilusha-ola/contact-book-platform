import re
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from app.db.session import get_database

def validate_email_format(email: str) -> bool:
    regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(regex, email))

def format_company_doc(doc: dict) -> dict:
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc

class CompanyRepository:
    def get_collection(self):
        db = get_database()
        return db["companies"] if db is not None else None

    async def get_all(
        self,
        name: Optional[str] = None,
        company_email: Optional[str] = None,
        location: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[dict]:
        col = self.get_collection()
        if col is None:
            return []

        filter_dict = {}

        if name:
            filter_dict["name"] = {"$regex": name, "$options": "i"}
        if company_email:
            filter_dict["company_email"] = {"$regex": company_email, "$options": "i"}
        if location:
            filter_dict["location"] = {"$regex": location, "$options": "i"}
        if query:
            regex_query = {"$regex": query, "$options": "i"}
            filter_dict["$or"] = [
                {"name": regex_query},
                {"company_email": regex_query},
                {"location": regex_query},
                {"phone": regex_query}
            ]

        cursor = col.find(filter_dict).sort("created_at", -1)
        companies = []
        async for doc in cursor:
            companies.append(format_company_doc(doc))
        return companies

    async def get_by_id(self, company_id: str) -> Optional[dict]:
        col = self.get_collection()
        if col is None or not ObjectId.is_valid(company_id):
            return None
        doc = await col.find_one({"_id": ObjectId(company_id)})
        return format_company_doc(doc)

    async def create(self, data: dict) -> dict:
        col = self.get_collection()
        data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["is_valid"] = validate_email_format(data.get("company_email", ""))

        result = await col.insert_one(data)
        data["id"] = str(result.inserted_id)
        data.pop("_id", None)
        return data

    async def update(self, company_id: str, update_data: dict) -> Optional[dict]:
        col = self.get_collection()
        if col is None or not ObjectId.is_valid(company_id):
            return None
        
        if "company_email" in update_data:
            update_data["is_valid"] = validate_email_format(update_data["company_email"])

        await col.update_one({"_id": ObjectId(company_id)}, {"$set": update_data})
        return await self.get_by_id(company_id)

    async def delete(self, company_id: str) -> bool:
        col = self.get_collection()
        if col is None or not ObjectId.is_valid(company_id):
            return False
        result = await col.delete_one({"_id": ObjectId(company_id)})
        return result.deleted_count > 0

    async def get_stats(self) -> dict:
        col = self.get_collection()
        if col is None:
            return {"total_companies": 0}
        total = await col.count_documents({})
        return {"total_companies": total}

company_repo = CompanyRepository()
