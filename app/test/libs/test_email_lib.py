import unittest
import requests_mock

from main.libs.email import Email
from test.conftest import register_mock_mailgun


class TestEmailLib(unittest.TestCase):
    @classmethod
    @requests_mock.Mocker()
    def test_send_email(cls, mock):
        register_mock_mailgun(mock)
        email = "michaelmcguiness123@gmail.com"
        subject = "Test Subject"
        text = "Test Text"
        html = "<html>Test HTML</html>"
        response = Email.send_email([email], subject, text, html)
        assert response.status_code == 200

    # def test_exception_thrown_without_api_key(self):
    #     email = Email()
    #
    #     email.MAILGUN_API_KEY = None
    #     self.assertRaises(EmailException, email.send_email([''], '', '', ''))
