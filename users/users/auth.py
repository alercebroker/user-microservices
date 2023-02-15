from fastapi import Depends
from .settings import GoogleOAuthSettings, get_google_settings
from ..utils.auth import GoogleOAuthClient

def get_google_auth_client(google_settings: GoogleOAuthSettings = Depends(get_google_settings)):
    auth_client = GoogleOAuthClient(google_settings)
    return auth_client
