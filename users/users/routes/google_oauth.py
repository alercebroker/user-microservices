from ..auth_clients import GoogleOAuthClient
from ..models import GoogleLoginIn
from ..helpers import create_user_token

from fastapi import Depends
from fastapi import APIRouter

router = APIRouter()

@router.post(
    "/o/google-oauth2"
)
async def login(GoogleLoginIn, client= Depends(GoogleOAuthClient.get_client)):
    token = await client.google.authorize_access_token(GoogleLoginIn)

    user_token = create_user_token()
    return user_token
