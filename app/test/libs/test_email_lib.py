import unittest

import requests_mock

from app.main.libs.email import Email

MAILGUN_URL = 'https://api.mailgun.net/v3/sandboxc3e6b65541ae41bc8bf153f612aa0b0d.mailgun.org/messages'


class TestEmailLib(unittest.TestCase):
    @classmethod
    @requests_mock.Mocker()
    def test_send_email(cls, mock_requests):
        mock_requests.post(
            MAILGUN_URL,
            text='resp')

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
