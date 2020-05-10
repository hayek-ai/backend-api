from unittest.mock import create_autospec

import requests
import requests_mock

import app
from app.main import create_app
from app.test.mock_responses import aapl_quote, aapl_company, aapl_chart, aapl_advanced_stats, aapl_alpha_advantage

MAILGUN_URL = 'https://api.mailgun.net/v3/'
IEX_URL = 'https://cloud.iexapis.com/v1/stock/AAPL'
ALPHA_ADVANTAGE_URL = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH'


def services_for_test(user=None, confirmation=None, idea=None, download=None,\
                      follow=None, review=None, comment=None):
    return {
        'user': user or create_autospec(app.main.UserService, spec_set=True, instance=True),
        'confirmation': confirmation or create_autospec(app.main.ConfirmationService, spec_set=True, instance=True),
        'idea': idea or create_autospec(app.main.IdeaService, spec_set=True, instance=True),
        'download': download or create_autospec(app.main.DownloadService, spec_set=True, instance=True),
        'follow': follow or create_autospec(app.main.FollowService, spec_set=True, instance=True),
        'review': review or create_autospec(app.main.ReviewService, spec_set=True, instance=True),
        'comment': comment or create_autospec(app.main.CommentService, spec_set=True, instance=True)
    }


def flask_test_client(services=None, environment="testing"):
    application = create_app(services or services_for_test(), environment)
    # If you try to perform database operations outside an application context, you get an error
    application.app_context().push()
    return application.test_client()


def requests_session():
    return requests.session()


def register_mock_mailgun(session):
    adapter = requests_mock.Adapter()

    adapter.register_uri('POST', MAILGUN_URL, text='resp')

    session.mount('https://', adapter)


def register_mock_iex(session):
    adapter = requests_mock.Adapter()

    # Register mock responses you want returned
    adapter.register_uri('GET', IEX_URL + '/quote', json=aapl_quote)
    adapter.register_uri('GET', IEX_URL + '/company', json=aapl_company)
    adapter.register_uri('GET', IEX_URL + '/chart', json=aapl_chart)
    adapter.register_uri('GET', IEX_URL + '/advanced-stats', json=aapl_advanced_stats)

    session.mount('https://', adapter)


def register_mock_alpha_advantage(session):
    adapter = requests_mock.Adapter()

    adapter.register_uri('GET', ALPHA_ADVANTAGE_URL + '&keywords=AAPL', json=aapl_alpha_advantage)

    session.mount('https://', adapter)
