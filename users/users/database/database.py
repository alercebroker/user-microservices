from datetime import datetime
from fastapi import Depends
from db_handler import MongoConnection, DocumentNotFound
from ..helpers import SingletonMetaClass
from .models import User, _utcnow
from ..settings import MongoSettings, get_mongo_settings

def get_mongo_client(settings: MongoSettings = Depends(get_mongo_settings)):
    client = MongoClient(settings)
    return client

class MongoClient(MongoConnection, meta=SingletonMetaClass):
    #Tiene que ser clase para heredar de mongo conection
    def __init__(self, config) -> None:
        super().__init__(self, config)

    async def get_user_by_email(self, email: str) -> dict:
        document = await self.db[User.__tablename__].find_one({"auth_source.email": email})
        if document is None:
            raise DocumentNotFound(email)
        return document

    async def get_user_by_username(self, username: str) -> dict:
        document = await self.db[User.__tablename__].find_one({"auth_source.username": username})
        if document is None:
            raise DocumentNotFound(username)
        return document

    async def create_user(self, user_dict: dict) -> dict:
        return await self.create_document(User, user_dict)

    async def set_verified(self, user_id: str, verified=True) -> bool:
        return await self.update_document(User, user_id, {"verified": verified})

    async def set_active(self, user_id: str, active=True) -> bool:
        return await self.update_document(User, user_id, {"active": active})

    async def update_last_login(self, user_id: str) -> dict:
        return await self.update_document(User, user_id, {"last_login": _utcnow()})
