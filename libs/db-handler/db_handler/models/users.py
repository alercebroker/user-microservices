from datetime import datetime

from pymongo import IndexModel
from pydantic import Field

from ..utils import BaseModelWithId


class User(BaseModelWithId):
    """Full mongo model for users personal and auth data"""
    __tablename__ = "users"
    __indexes__ = [
        IndexModel([("email", -1)])
    ]
    

    name: str = Field(..., description="Name of the user")
    email: str = Field(..., description="Email associated with the account")
