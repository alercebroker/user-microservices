import unittest
from unittest import mock
from datetime import datetime, timedelta
import jwt
from utils.jwt import JWTHelper

TEST_SECRET_KEY = "a_secret_key"
TEST_AUTH_TOKEN_DURATION = 60
TEST_REFRESH_TOKEN_DURATION = 90
TEST_SETTINGS_DICT = {
        "secret_key": TEST_SECRET_KEY,
        "auth_token_duration": TEST_AUTH_TOKEN_DURATION,
        "refresh_token_duration": TEST_REFRESH_TOKEN_DURATION
    }

class JWTHelperTestCase(unittest.TestCase):
    
    auth_helper = JWTHelper(TEST_SETTINGS_DICT)

    def get_shifted_timestamp(self, delta_seconds, positive=True):
        if positive:
            shifted_dt = datetime.now() + timedelta(seconds=delta_seconds)
        else:
            shifted_dt = datetime.now() - timedelta(seconds=delta_seconds)
        return int(shifted_dt.timestamp())
        
    def encrypt_test_token(self, token):
        token = jwt.encode(token, key=TEST_SECRET_KEY, algorithm="HS256")
        return token

    def decrypt_token(self, token):
        content = jwt.decode(
            token,
            key=TEST_SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_signature": False}
        )
        return content

    def test_geting_corrects_tokens(self):
        # for user token
        auth_exp_time = self.get_shifted_timestamp(TEST_AUTH_TOKEN_DURATION)
        with mock.patch('utils.jwt.get_expiration_time') as mock_get_exp:
            mock_get_exp.return_value = auth_exp_time
            test_user_token = self.auth_helper.create_user_token(123)
        decrypted_user_token = self.decrypt_token(test_user_token)
        expected_token_content = {
            "user_id": 123,
            "iss": "Users Microservice",
            "exp": auth_exp_time
        }
        self.assertDictEqual(decrypted_user_token, expected_token_content)

        # for refresh token
        refresh_exp_time = self.get_shifted_timestamp(seconds=TEST_REFRESH_TOKEN_DURATION)
        with mock.patch('utils.jwt.get_expiration_time') as mock_get_exp:
            mock_get_exp.return_value = refresh_exp_time
            test_refresh_token = self.auth_helper.create_refresh_token(456)
        decrypted_refresh_token = self.decrypt_token(test_refresh_token)
        expected_token_content = {
            "user_id": 456,
            "iss": "Users Microservice",
            "exp": refresh_exp_time
        }
        self.assertDictEqual(decrypted_refresh_token, expected_token_content)

    def test_decrypt_correct_token(self):
        # for user token
        user_exp_time = self.get_shifted_timestamp(60)
        test_user_token = {
            "user_id": 321,
            "iss": "unittest",
            "exp": user_exp_time
        }
        encrypted_test_token = self.encrypt_test_token(test_user_token)
        decrypted_test_token = self.auth_helper.decrypt_user_token(encrypted_test_token)
        self.assertDictEqual(decrypted_test_token, test_user_token)

        # for refresh token
        refresh_exp_time = self.get_shifted_timestamp(60)
        test_refresh_token = {
            "user_id": 321,
            "iss": "unittest",
            "exp": refresh_exp_time
        }
        encrypted_test_token = self.encrypt_test_token(test_refresh_token)
        decrypted_test_token = self.auth_helper.decrypt_refresh_token(encrypted_test_token)
        self.assertDictEqual(decrypted_test_token, test_refresh_token)

    def test_decrypt_incorrect_token(self):
        # for user token
        auth_exp_time = self.get_shifted_timestamp(60)
        test_incomplete_user_token = {
            "iss": "unittest",
            "exp": auth_exp_time
        }
        encrypted_test_token = self.encrypt_test_token(test_incomplete_user_token)
        with self.assertRaises(jwt.MissingRequiredClaimError):
            self.auth_helper.decrypt_user_token(encrypted_test_token)

        # for refresh token
        refresh_exp_time = self.get_shifted_timestamp(60)
        test_incomplete_user_token = {
            "iss": "unittest",
            "exp": refresh_exp_time
        }
        encrypted_test_token = self.encrypt_test_token(test_incomplete_user_token)
        with self.assertRaises(jwt.MissingRequiredClaimError):
            self.auth_helper.decrypt_refresh_token(encrypted_test_token)


    def test_decrypt_expired_token(self):
        # for user token
        auth_exp_time = self.get_shifted_timestamp(60, positive=False)
        test_expired_user_token = {
            "user_id": 111,
            "iss": "unittest",
            "exp": auth_exp_time
        }
        encrypted_test_token = self.encrypt_test_token(test_expired_user_token)
        with self.assertRaises(jwt.ExpiredSignatureError):
            self.auth_helper.decrypt_refresh_token(encrypted_test_token)

        # for refresh token
        refresh_exp_time = self.get_shifted_timestamp(60, positive=False)
        test_expired_refresh_token = {
            "user_id": 222,
            "iss": "unittest",
            "exp": refresh_exp_time
        }
        encrypted_test_token = self.encrypt_test_token(test_expired_refresh_token)
        with self.assertRaises(jwt.ExpiredSignatureError):
            self.auth_helper.decrypt_refresh_token(encrypted_test_token)
