from fastapi import Depends
from .settings import ServerSettings, get_server_settings
from ..utils.jwt import JWTHelper

def get_jwt_helper(jwt_setings: ServerSettings = Depends(get_server_settings)):
    jwt_helper = JWTHelper(jwt_setings)
    return jwt_helper
