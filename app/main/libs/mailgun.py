import os
from typing import List
from requests import Response, post

from app.main.libs.strings import gettext


class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", None)
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", None)

    FROM_TITLE = "hayek.ai"
    FROM_EMAIL = f"no-reply@{MAILGUN_DOMAIN}"

    @classmethod
    def send_email(
        cls, email: List[str], subject: str, text: str, html: str
    ) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailgunException(gettext("mailgun_failed_load_api_key"))

        if cls.MAILGUN_API_KEY is None:
            raise MailgunException(gettext("mailgun_failed_load_domain"))

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
            raise MailgunException(gettext("mailgun_error_send_email"))

        return response
