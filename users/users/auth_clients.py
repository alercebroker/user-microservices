from authlib.integrations.starlette_client import OAuth

class GoogleOAuthClient(object):
    oauth = OAuth(

    )
    oauth.register(
        "google"
    )

    def get_client(self):
        return self.oauth