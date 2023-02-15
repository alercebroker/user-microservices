from datetime import datetime, timezone
from pydantic import BaseModel, Field
from pymongo import IndexModel
from db_handler import PyObjectId, ModelMetaclass


def _oid() -> PyObjectId:
    # duplicado poner en libreria
    return PyObjectId()

def _utcnow() -> datetime:
    # duplicado poner en libreria
    now = datetime.now(timezone.utc)
    # Needed to keep in line with format allowed in MongoDB (millisecond resolution, unmarked TZ)
    # why?
    return now.replace(microsecond=(now.microsecond // 1000) * 1000, tzinfo=None)


class AuthModel(BaseModel):
    username: str = Field(..., description="")
    email: str = Field(..., description="")

class GoogleAuth(AuthModel):
    name: str = "google_auth2"

class PasswordAuth(AuthModel):
    name: str = "password_auth"
    password: str = Field(..., description="")

class User(BaseModel, metaclass=ModelMetaclass):
    __tablename__ = "users"
    __indexes__ = [IndexModel([("auth_source.email", 1)])]
    
    id: PyObjectId = Field(default_factory=_oid, description="")
    first_name: str = Field(..., description="")
    last_name: str = Field(..., description="")
    institution: str = Field(..., description="")
    auth_source: AuthModel = Field(..., description="")
    created_at: datetime = Field(_utcnow, description="")
    last_login: datetime = Field(_utcnow, description="")
