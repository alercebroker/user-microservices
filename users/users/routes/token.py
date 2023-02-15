
from db_handler import DocumentNotFound
from ..dependencies import get_mongo_client, get_jwt_helper
from ..models import TokenIn, RefreshIn

from fastapi import APIRouter, Depends

router = APIRouter()


@router.get(
    "/current"
)
async def current_user(
    TokenIn,
    db_client=Depends(get_mongo_client),
    helper=Depends(get_jwt_helper)
):
    token_content = helper.decrypt_user_token(TokenIn.token)
    user = db_client.get_user_by_id(token_content["user_id"])
    return user

@router.post(
    "/verify"
)
async def verify_token(
    TokenIn,
    helper=Depends(get_jwt_helper)
):
    # es necesario revisar que el user id existe?
    valid = helper.verify_user_token(TokenIn.token)
    # todo, definir schema para este boolean
    return {
        "valid": valid
    }

@router.post(
    "/refresh"
)
async def refresh_token(
    TokenIn,
    db_client=Depends(get_mongo_client),
    helper=Depends(get_jwt_helper)
):
    token_content = helper.decrypt_user_token(TokenIn.token)
    user = db_client.get_user_by_id(token_content["user_id"])
    new_token = helper.create_refresh_token(user)
    return new_token