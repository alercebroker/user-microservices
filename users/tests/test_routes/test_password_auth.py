import unittest
from unittest import mock
from fastapi.testclient import TestClient
from bcrypt import gensalt, hashpw
from users.users.main import app
from users.users.dependencies import get_server_settings
from users.users.routes.password_auth import get_mongo_client
from db_handler import DocumentNotFound

def override_server_settings():
    return {
        "secret_key": "a_secret_key",
        "auth_token_duration": 60,
        "refresh_token_duration": 600,
        "port": 5000
    }

app.dependency_overrides[get_server_settings] = override_server_settings

class PasswordAuthTestCase(unittest.TestCase):

    def test_create_user(self):
        client = TestClient(app)

        new_user = {
            "first_name": "user",
            "last_name": "new",
            "email": "email@dom.dom",
            "username": "new_user",
            "password": "abc123"
        }
        mock_mongo_client = mock.Mock()
        mock_mongo_client.get_user_by_username.side_effect = DocumentNotFound("new_user")
        mock_mongo_client.create_new_user.return_value = {
            "id": "id123"
        }
        def override_get_mongo_client():
            return mock_mongo_client
        
        app.dependency_overrides[get_mongo_client] = override_get_mongo_client
        response = client.post("/user", json=new_user)

        mock_mongo_client.get_user_by_username.assert_called_once_with("new_user")
        mock_mongo_client.create_new_user.assert_called_once() # problema para call_with -> password
        self.assertEqual(response.status_code, 200) # check el code

    def test_login_user(self,):
        client = TestClient(app)

        login_credentials = {
            "username": "existing_user",
            "password": "abc123"
        }
        mock_mongo_client = mock.Mock()
        mock_mongo_client.get_user_by_username.return_value = {
            "id": "id123",
            "auth_source": {
                "password": hashpw("abc123".encode(), gensalt())
            }
        }
        def override_get_mongo_client():
            return mock_mongo_client
        
        app.dependency_overrides[get_mongo_client] = override_get_mongo_client
        response = client.post("/user/login", json=login_credentials)

        mock_mongo_client.get_user_by_username.assert_called_once_with("existing_user")
        self.assertEqual(response.status_code, 200)

    def test_bad_user_form(self):
        client = TestClient(app)
        
        # user exists
        new_user = {
            "first_name": "user",
            "last_name": "new",
            "email": "email@dom.dom",
            "username": "new_user",
            "password": "abc123"
        }
        mock_mongo_client = mock.Mock()
        mock_mongo_client.get_user_by_username.return_value = {"id": "id123"}
        def override_get_mongo_client():
            return mock_mongo_client
        
        app.dependency_overrides[get_mongo_client] = override_get_mongo_client
        response = client.post("/user", json=new_user)

        mock_mongo_client.get_user_by_username.assert_called_once_with("new_user")
        self.assertEqual(response.status_code, 400) # check el code
        
        # missing params
        client = TestClient(app)

        new_user_missing_params = {
            "email": "email@dom.dom",
            "username": "new_user",
            "password": "abc123"
        }
        mock_mongo_client = mock.Mock()
        mock_mongo_client.get_user_by_username.side_effect = DocumentNotFound("new_user")
        mock_mongo_client.create_new_user.return_value = {
            "id": "id123"
        }
        def override_get_mongo_client():
            return mock_mongo_client
        
        app.dependency_overrides[get_mongo_client] = override_get_mongo_client
        response = client.post("/user", json=new_user_missing_params)

        self.assertEqual(response.status_code, 422) # revisar que deberia retornar

    def test_bad_login(self):
        client = TestClient(app)

        # user dont exists
        login_credentials_user_not_found = {
            "username": "not_existing_user",
            "password": "abc123"
        }
        mock_mongo_client = mock.Mock()
        mock_mongo_client.get_user_by_username.side_effect = DocumentNotFound("new_user")
        def override_get_mongo_client():
            return mock_mongo_client
        
        app.dependency_overrides[get_mongo_client] = override_get_mongo_client
        response = client.post("/user/login", json=login_credentials_user_not_found)

        mock_mongo_client.get_user_by_username.assert_called_once_with("not_existing_user")
        self.assertEqual(response.status_code, 404)

        # cant validate login
        client = TestClient(app)

        login_credentials = {
            "username": "existing_user",
            "password": "abc123"
        }
        mock_mongo_client = mock.Mock()
        mock_mongo_client.get_user_by_username.return_value = {
            "id": "id123",
            "auth_source": {
                "password": hashpw("def456".encode(), gensalt())
            }
        }
        def override_get_mongo_client():
            return mock_mongo_client
        
        app.dependency_overrides[get_mongo_client] = override_get_mongo_client
        response = client.post("/user/login", json=login_credentials)

        mock_mongo_client.get_user_by_username.assert_called_once_with("existing_user")
        self.assertEqual(response.status_code, 400) # revisar que hacer con este codigo
