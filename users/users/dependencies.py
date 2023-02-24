from fastapi import Depends
from users.users.settings import (
    MongoSettings, get_mongo_settings,
    GoogleOAuthSettings,
    get_google_settings,
    ServerSettings,
    get_server_settings
    )
from users.database import MongoClient
from users.utils.auth import GoogleOAuthClient, PasswordAuthClient
from users.utils.jwt import JWTHelper

def get_mongo_client(settings: MongoSettings = Depends(get_mongo_settings)):
    client = MongoClient(settings)
    return client

def get_google_auth_client(google_settings: GoogleOAuthSettings = Depends(get_google_settings)):
    auth_client = GoogleOAuthClient(google_settings)
    return auth_client

def get_jwt_helper(jwt_setings: ServerSettings = Depends(get_server_settings)):
    jwt_helper = JWTHelper(jwt_setings)
    return jwt_helper

def get_password_auth_client():
    auth_client = PasswordAuthClient()
    return auth_client
