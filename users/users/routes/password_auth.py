from fastapi import HTTPException

from db_handler import DocumentNotFound
from users.users.dependencies import get_password_auth_client, get_mongo_client, get_jwt_helper
from users.users.models import NewUserIn, PasswordLoginIn

from fastapi import APIRouter, Depends

router = APIRouter()

@router.post(
    "/user"
)
async def new_user(
    new_user: NewUserIn,
    auth_client=Depends(get_password_auth_client),
    db_client=Depends(get_mongo_client),
    helper=Depends(get_jwt_helper)
):
    # check if user exists
    try:
        user = db_client.get_user_by_username(new_user.username)
        raise HTTPException(status_code=400, detail="User exist")
    except DocumentNotFound:
        # create new user
        new_user_dict = {
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "auth_source": {
                "name": "password_auth",
                "username": new_user.username,
                "email": new_user.email,
                "password": auth_client.generate_new_password_hash(new_user.password)
            }
        }
        user = db_client.create_new_user(new_user_dict)

    user_token = helper.create_user_token(user["id"])
    refresh_token = helper.create_refresh_token(user["id"])    
    
    return {
        "access": user_token,
        "refresh": refresh_token
    }

@router.post(
    "/user/login"
)
async def login(
    login: PasswordLoginIn,
    auth_client=Depends(get_password_auth_client),
    db_client=Depends(get_mongo_client),
    helper=Depends(get_jwt_helper)
):
    user = db_client.get_user_by_username(login.username)
    match = auth_client.validate_password(login.password, user["auth_source"]["password"])
    if match:
        user_token = helper.create_user_token(user["id"])
        refresh_token = helper.create_refresh_token(user["id"])    
    
        return {
            "access": user_token,
            "refresh": refresh_token
        }
    else:
        # password o user malo
        raise HTTPException(status_code=400)
