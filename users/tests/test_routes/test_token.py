import unittest
from unittest import mock
from fastapi.testclient import TestClient
from users.users.main import app
from users.users.dependencies import get_server_settings
from users.users.routes.token import get_mongo_client
from db_handler import DocumentNotFound
import jwt
from datetime import datetime, timedelta


def create_token(user_id, iss=None, exp=None):
    payload = {
        "user_id": user_id
    }
    if iss:
        payload["iss"] = iss
    if exp:
        payload["exp"] = exp
    
    token = jwt.encode(payload, key="a_secret_key", algorithm="HS256")
    return token

def get_shifted_timestamp(delta_seconds, positive=True):
    if positive:
        shifted_dt = datetime.now() + timedelta(seconds=delta_seconds)
    else:
        shifted_dt = datetime.now() - timedelta(seconds=delta_seconds)
    return int(shifted_dt.timestamp())

def override_server_settings():
    return {
        "secret_key": "a_secret_key",
        "auth_token_duration": 60,
        "refresh_token_duration": 600,
        "port": 5000
    }

app.dependency_overrides[get_server_settings] = override_server_settings

class TokenRouteTestCase(unittest.TestCase):
    
    def test_current(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", "Unittest", get_shifted_timestamp(60))
        }
        mock_mongo_client = mock.Mock()
        mock_mongo_client.get_user_by_id.return_value = {
            "id": "id123"
        }
        def override_get_mongo_client():
            return mock_mongo_client
        
        app.dependency_overrides[get_mongo_client] = override_get_mongo_client
        response = client.post("/current", json=token)

        mock_mongo_client.get_user_by_id.assert_called_once_with("id123")
        self.assertEqual(response.status_code, 200) # check el code

    def test_verify(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", "Unittest", get_shifted_timestamp(60))
        }
        response = client.post("/verify", json=token)

        self.assertEqual(response.status_code, 200) # check el code

    def test_refresh(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", "Unittest", get_shifted_timestamp(60))
        }
        mock_mongo_client = mock.Mock()
        mock_mongo_client.get_user_by_id.return_value = {
            "id": "id123"
        }
        def override_get_mongo_client():
            return mock_mongo_client
        
        app.dependency_overrides[get_mongo_client] = override_get_mongo_client
        response = client.post("/refresh", json=token)

        mock_mongo_client.get_user_by_id.assert_called_once_with("id123")
        self.assertEqual(response.status_code, 200) # check el code

    def test_current_token_expired(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", "Unittest", get_shifted_timestamp(60, positive=False))
        }
        response = client.post("/current", json=token)

        self.assertEqual(response.status_code, 400) # check el code

    def test_current_user_not_found(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", "Unittest", get_shifted_timestamp(60))
        }
        mock_mongo_client = mock.Mock()
        mock_mongo_client.get_user_by_id.side_effect = DocumentNotFound("id123")
        
        def override_get_mongo_client():
            return mock_mongo_client
        
        app.dependency_overrides[get_mongo_client] = override_get_mongo_client
        response = client.post("/current", json=token)

        mock_mongo_client.get_user_by_id.assert_called_once_with("id123")
        self.assertEqual(response.status_code, 404) # check el code

    def test_current_user_token_missing_field(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", exp=get_shifted_timestamp(60))
        }
        response = client.post("/current", json=token)

        self.assertEqual(response.status_code, 403) # check el code

    def test_verify_token_expired(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", "Unittest", get_shifted_timestamp(60, positive=False))
        }
        response = client.post("/verify", json=token)

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {"valid": False})

    def test_verify_token_missing_field(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", exp=get_shifted_timestamp(60))
        }
        response = client.post("/verify", json=token)

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {"valid": False})

    def test_refresh_token_expired(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", "Unittest", get_shifted_timestamp(60, positive=False))
        }
        response = client.post("/refresh", json=token)

        self.assertEqual(response.status_code, 400) # check el code

    def test_refresh_user_not_found(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", "Unittest", get_shifted_timestamp(60))
        }
        mock_mongo_client = mock.Mock()
        mock_mongo_client.get_user_by_id.side_effect = DocumentNotFound("id123")
        def override_get_mongo_client():
            return mock_mongo_client
        
        app.dependency_overrides[get_mongo_client] = override_get_mongo_client
        response = client.post("/refresh", json=token)

        mock_mongo_client.get_user_by_id.assert_called_once_with("id123")
        self.assertEqual(response.status_code, 404) # check el code

    def test_refresh_user_token_missing_field(self):
        client = TestClient(app)

        token = {
            "token": create_token("id123", exp = get_shifted_timestamp(60))
        }
        response = client.post("/refresh", json=token)

        self.assertEqual(response.status_code, 403) # check el code
