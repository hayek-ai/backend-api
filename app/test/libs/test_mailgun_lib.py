import unittest

from app.main.libs.mailgun import Mailgun


class TestMailgunLib(unittest.TestCase):
    @classmethod
    def test_send_email(cls):
        email="michaelmcguiness123@gmail.com"
        subject = "Test Subject"
        text = "Test Text"
        html = "<html>Test HTML</html>"
        response = Mailgun.send_email([email], subject, text, html)
        assert response.status_code == 200
