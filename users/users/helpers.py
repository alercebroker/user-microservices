from pydantic import Any
from fastapi import Depends
import jwt
from .settings import ServerSettings, get_server_settings
from .database import User

class SingletonMetaClass(type):
    # mover a lib
    _instances = {}

    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwds)
            cls._instances[cls] = instance
        return cls._instances[cls]

class JWTHelper(object):

    required_auth_token_fields = [
        "user_id",
        "iss",
        "exp"
    ]
    required_refresh_token_fields = [
        "user_id",
        "iss",
        "exp"
    ]

    def __init__(self, settings: ServerSettings) -> None:
        self.settings = settings

    def create_user_token(self, user: User):
        token_payload = {
            "user_id": user.id,
            "iss": "h",
            "exp": 1
        }
        token = jwt.encode(token_payload, key=self.settings.secret_key, algorithm="HS256")
        return token

    def create_refresh_token(self, user: User):
        token_payload = {
            "user_id": user.id,
            "iss": "h",
            "exp": 1
        }
        token = jwt.encode(token_payload, key=self.settings.secret_key, algorithm="HS256")
        return token
    
    def _verify_token(self, token:str, required_fields: list[str]):
        try:
            jwt.decode(
                token,
                key=self.settings.secret_key,
                algorithms=["HS256"],
                options={
                    "require": required_fields
                }
            )
        except:
            return False

        return True
    
    def _decrypt_token(self, token: str, required_fields: list[str]):
        decrypted_token = jwt.decode(
            token,
            key=self.settings.secret_key,
            algorithms=["HS256"],
            options={
                "require": required_fields
            }
        )
        return decrypted_token
    
    def verify_user_token(self, token: str):
        return self._verify_token(token, self.required_auth_token_fields)

    def verify_refresh_token(self, token: str):
        return self._verify_token(token, self.required_refresh_token_fields)

    def decrypt_user_token(self, token: str):
        # duda aqui: Hacemos diferencia entre errores de token malo o token expirado?
        return self._decrypt_token(token, self.required_auth_token_fields)
    
    def decrypt_refresh_token(self, token:str):
        return self._decrypt_token(token, self.required_refresh_token_fields)

def get_jwt_helper(settings: ServerSettings = Depends(get_server_settings)):
    helper = JWTHelper(settings)
    return helper
