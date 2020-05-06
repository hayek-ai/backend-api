import unittest

from app.main.libs.email import Email


class TestEmailLib(unittest.TestCase):
    @classmethod
    def test_send_email(cls):
        email = "michaelmcguiness123@gmail.com"
        subject = "Test Subject"
        text = "Test Text"
        html = "<html>Test HTML</html>"
        response = Email.send_email([email], subject, text, html)
        assert response.status_code == 200
