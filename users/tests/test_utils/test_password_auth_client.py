import unittest
from bcrypt import gensalt, hashpw, checkpw
from utils.auth import PasswordAuthClient

TEST_PASSWORD = "a_password"

class PasswordAuwhTestCase(unittest.TestCase):
    
    password_auth_client = PasswordAuthClient()

    def test_hash_password(self):
        test_hash = self.password_auth_client.generate_new_password_hash(TEST_PASSWORD)
        self.assertTrue(checkpw(TEST_PASSWORD.encode(), test_hash))

    def test_validate_correct_password(self):
        hashed_password = hashpw(TEST_PASSWORD.encode(), gensalt())
        self.assertTrue(self.password_auth_client.validate_password(TEST_PASSWORD, hashed_password))

    def test_validate_incorrect_password(self):
        hashed_password = hashpw(TEST_PASSWORD.encode(), gensalt())
        self.assertFalse(self.password_auth_client.validate_password("not_a_password", hashed_password))
