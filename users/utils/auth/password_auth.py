from bcrypt import gensalt, hashpw, checkpw

class PasswordAuthClient(object):
    
    def __init__(self, settings) -> None:
        self.settings = settings

    def generate_new_password_hash(self, password_string):
        hashed_password = hash(password_string, gensalt())
        return hashed_password

    def validate_password(self, password_string, stored_password):
        match = checkpw(password_string, stored_password)
        return match
