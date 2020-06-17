import unittest
from main.libs.security import encrypt_password, check_encrypted_password


class TestSecurityLib(unittest.TestCase):
    @classmethod
    def test_password_encryption(cls):
        assert encrypt_password("password") != "password"
        assert check_encrypted_password("password", encrypt_password("password")) is True
        assert check_encrypted_password("password1", encrypt_password("password")) is False

