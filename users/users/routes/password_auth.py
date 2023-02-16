from fastapi import HTTPException

from db_handler import DocumentNotFound
from ..dependencies import get_password_auth_client, get_mongo_client, get_jwt_helper
from ..models import NewUserIn, PasswordLoginIn

from fastapi import APIRouter, Depends

router = APIRouter()

@router.post(
    "/user"
)
async def new_user():
    pass

@router.post(
    "/user/login"
)
async def login():
    pass
