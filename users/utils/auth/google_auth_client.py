from authlib.integrations.starlette_client import OAuth
from ..singleton_helper import SingletonMetaClass

class GoogleOAuthClient(object, metaclass=SingletonMetaClass):
    oauth = None
    
    def __init__(self, config) -> None:    
        oauth = OAuth(
            config=config
        )
        oauth.register(
            "google"
        )

    def get_user_data(self, token: str) -> dict:
        google_response = self.oauth.google.authorize_access_token(token)
        return google_response
