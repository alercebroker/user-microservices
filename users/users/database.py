from fastapi import Depends
from .settings import MongoSettings, get_mongo_settings
from ..database import MongoClient

def get_mongo_client(settings: MongoSettings = Depends(get_mongo_settings)):
    client = MongoClient(settings)
    return client