import unittest

from fastapi.security import HTTPAuthorizationCredentials

from app.middleware.auth import get_current_user


class TestAuthMiddleware(unittest.TestCase):
    def test_get_current_user_returns_compatibility_keys(self):
        original = __import__('app.middleware.auth', fromlist=['decode_access_token']).decode_access_token
        __import__('app.middleware.auth', fromlist=['decode_access_token']).decode_access_token = lambda token: {"sub": "42", "role": "Employee"}
        try:
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="dummy-token")
            user = get_current_user(credentials)
            self.assertEqual(user["id"], 42)
            self.assertEqual(user["user_id"], 42)
            self.assertEqual(user["role"], "Employee")
        finally:
            __import__('app.middleware.auth', fromlist=['decode_access_token']).decode_access_token = original


if __name__ == "__main__":
    unittest.main()
