from authlib.integrations.starlette_client import OAuth
from .helpers import SingletonMetaClass

class GoogleOAuthClient(object, meta=SingletonMetaClass):
    oauth = None
    
    def __init__(self) -> None:    
        oauth = OAuth(

        )
        oauth.register(
            "google"
        )

    def get_client(self):
        return self.oauth