
from bcrypt import gensalt, hashpw, checkpw

class PasswordAuthClient(object):
    
    def __init__(self, settings) -> None:
        pass

    
    def generate_new_password_hash(self, password_string: str):
        salt = gensalt()
        hashed_password = hashpw(password_string.encode(), salt)
        return hashed_password

    def validate_password(self, password_string: str, stored_password: str):
        match = checkpw(password_string.encode(), stored_password)
        return match
