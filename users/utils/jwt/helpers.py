import jwt
# no se tiene que importar user, los metodos van a pedir todos los campos

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

    def __init__(self, settings: dict) -> None:
        self.settings = settings

    def _create_token(self, payload: dict):
        token = jwt.encode(payload, key=self.settings.secret_key, algorithm="HS256")
        return token

    def create_user_token(self, user_id):
        token_payload = {
            "user_id": user_id,
            "iss": "h",
            "exp": 1
        }
        return self._create_token(token_payload)

    def create_refresh_token(self, user_id):
        token_payload = {
            "user_id": user_id,
            "iss": "h",
            "exp": 1
        }
        return self._create_token(token_payload)
    
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
