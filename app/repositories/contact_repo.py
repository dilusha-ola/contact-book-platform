import re
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from app.db.session import get_database

def validate_email_format(email: str) -> bool:
    regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(regex, email))

def format_contact_doc(doc: dict) -> dict:
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc

class ContactRepository:
    def get_collection(self):
        db = get_database()
        return db["contacts"] if db is not None else None

    async def get_all(self, query: Optional[str] = None, category: Optional[str] = None) -> List[dict]:
        col = self.get_collection()
        if col is None:
            return []

        filter_dict = {}
        if query:
            regex_query = {"$regex": query, "$options": "i"}
            filter_dict["$or"] = [
                {"name": regex_query},
                {"email": regex_query},
                {"company": regex_query}
            ]
        if category and category != "All":
            filter_dict["category"] = {"$regex": f"^{category}$", "$options": "i"}

        cursor = col.find(filter_dict).sort("created_at", -1)
        contacts = []
        async for doc in cursor:
            contacts.append(format_contact_doc(doc))
        return contacts

    async def get_by_id(self, contact_id: str) -> Optional[dict]:
        col = self.get_collection()
        if col is None or not ObjectId.is_valid(contact_id):
            return None
        doc = await col.find_one({"_id": ObjectId(contact_id)})
        return format_contact_doc(doc)

    async def create(self, data: dict) -> dict:
        col = self.get_collection()
        data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["is_valid"] = validate_email_format(data["email"])
        result = await col.insert_one(data)
        data["id"] = str(result.inserted_id)
        data.pop("_id", None)
        return data

    async def update(self, contact_id: str, update_data: dict) -> Optional[dict]:
        col = self.get_collection()
        if col is None or not ObjectId.is_valid(contact_id):
            return None
        
        if "email" in update_data:
            update_data["is_valid"] = validate_email_format(update_data["email"])

        await col.update_one({"_id": ObjectId(contact_id)}, {"$set": update_data})
        return await self.get_by_id(contact_id)

    async def delete(self, contact_id: str) -> bool:
        col = self.get_collection()
        if col is None or not ObjectId.is_valid(contact_id):
            return False
        result = await col.delete_one({"_id": ObjectId(contact_id)})
        return result.deleted_count > 0

    async def get_stats(self) -> dict:
        col = self.get_collection()
        if col is None:
            return {"total_contacts": 0, "total_companies": 0, "work_contacts": 0, "personal_contacts": 0}

        total = await col.count_documents({})
        companies_pipeline = [{"$group": {"_id": "$company"}}, {"$match": {"_id": {"$ne": None}}}]
        companies = len(await col.aggregate(companies_pipeline).to_list(length=1000))
        work = await col.count_documents({"category": {"$regex": "^work$", "$options": "i"}})
        personal = await col.count_documents({"category": {"$regex": "^personal$", "$options": "i"}})
        return {
            "total_contacts": total,
            "total_companies": companies,
            "work_contacts": work,
            "personal_contacts": personal
        }

contact_repo = ContactRepository()
