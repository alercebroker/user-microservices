from cryptography.fernet import Fernet
from bcrypt import gensalt, hashpw, checkpw

class PasswordAuthClient(object):
    
    def __init__(self, settings) -> None:
        self.settings = settings
        self.fernet = Fernet(self.settings.secret_key)

    def generate_new_password_hash(self, password_string):
        encrypted_password = self.fernet.encrypt(password_string)
        hashed_password = hashpw(encrypted_password, gensalt())
        return hashed_password

    def validate_password(self, password_string, stored_password):
        encrypted_password_input = self.fernet.encrypt(password_string)
        match = checkpw(encrypted_password_input, stored_password)
        return match
