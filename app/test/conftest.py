from unittest.mock import create_autospec

import requests
import requests_mock

import app
from app.main import create_app


def services_for_test(user=None, confirmation=None, idea=None, download=None, follow=None):
    return {
        'user': user or create_autospec(app.main.UserService, spec_set=True, instance=True),
        'confirmation': confirmation or create_autospec(app.main.ConfirmationService, spec_set=True, instance=True),
        'idea': idea or create_autospec(app.main.IdeaService, spec_set=True, instance=True),
        'download': download or create_autospec(app.main.DownloadService, spec_set=True, instance=True),
        'follow': follow or create_autospec(app.main.FollowService, spec_set=True, instance=True)
    }


def flask_test_client(services=None, environment="testing"):
    application = create_app(services or services_for_test(), environment)
    # If you try to perform database operations outside an application context, you get an error
    application.app_context().push()
    return application.test_client()


def mock_mailgun_send_email():
    adapter = requests_mock.Adapter()
    MAILGUN_URL = 'https://api.mailgun.net/v3/sandboxc3e6b65541ae41bc8bf153f612aa0b0d.mailgun.org/messages'
    adapter.register_uri('POST', MAILGUN_URL, text='resp')
    session = requests.Session()
    session.mount('https://', adapter)
