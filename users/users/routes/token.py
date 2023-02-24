
from db_handler import DocumentNotFound
from users.users.dependencies import get_mongo_client, get_jwt_helper
from users.users.models import TokenIn, RefreshIn

from fastapi import APIRouter, Depends

router = APIRouter()


@router.post(
    "/current"
)
async def current_user(
    token: TokenIn,
    db_client=Depends(get_mongo_client),
    helper=Depends(get_jwt_helper)
):
    token_content = helper.decrypt_user_token(token.token)
    user = db_client.get_user_by_id(token_content["user_id"])
    return user

@router.post(
    "/verify"
)
async def verify_token(
    token: TokenIn,
    helper=Depends(get_jwt_helper)
):
    # es necesario revisar que el user id existe?
    valid = helper.verify_user_token(token.token)
    # todo, definir schema para este boolean
    return {
        "valid": valid
    }

@router.post(
    "/refresh"
)
async def refresh_token(
    token: RefreshIn,
    db_client=Depends(get_mongo_client),
    helper=Depends(get_jwt_helper)
):
    token_content = helper.decrypt_user_token(token.token)
    user = db_client.get_user_by_id(token_content["user_id"])
    new_token = helper.create_user_token(user["id"])
    return new_token