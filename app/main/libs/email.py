import os
from typing import List

from requests import Response, post

from main.libs.strings import get_text


class EmailException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Email:
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", None)
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", None)

    FROM_TITLE = "hayek.ai"
    FROM_EMAIL = f"no-reply@{MAILGUN_DOMAIN}"

    @classmethod
    def send_email(cls, email: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise EmailException(get_text("env_fail").format("Mailgun API Key"))

        if cls.MAILGUN_DOMAIN is None:
            raise EmailException(get_text("env_fail").format("Mailgun Domain"))

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html,
            }
        )

        if response.status_code != 200:
            raise EmailException(get_text("error_sending_email"))

        return response
