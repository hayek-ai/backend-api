from unittest.mock import create_autospec

import app
from app.main import create_app
from app.test.mock_responses import aapl_quote, aapl_company, aapl_chart, aapl_advanced_stats, aapl_alpha_advantage, \
    gm_advanced_stats, gm_chart, gm_quote, gm_company, gm_alpha_advantage

MAILGUN_URL = 'https://api.mailgun.net/v3/sandboxc3e6b65541ae41bc8bf153f612aa0b0d.mailgun.org/messages'
IEX_URL = 'https://sandbox.iexapis.com/v1/stock'
ALPHA_ADVANTAGE_URL = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH'


def services_for_test(user=None, confirmation=None, password_reset=None, idea=None,
                      download=None, follow=None, review=None, comment=None,\
                      upvote=None, downvote=None, bookmark=None):
    return {
        'user': user or create_autospec(app.main.UserService, spec_set=True, instance=True),
        'confirmation': confirmation or create_autospec(app.main.ConfirmationService, spec_set=True, instance=True),
        'password_reset': password_reset or create_autospec(app.main.PasswordResetService, spec_set=True, instance=True),
        'idea': idea or create_autospec(app.main.IdeaService, spec_set=True, instance=True),
        'download': download or create_autospec(app.main.DownloadService, spec_set=True, instance=True),
        'follow': follow or create_autospec(app.main.FollowService, spec_set=True, instance=True),
        'review': review or create_autospec(app.main.ReviewService, spec_set=True, instance=True),
        'comment': comment or create_autospec(app.main.CommentService, spec_set=True, instance=True),
        'upvote': upvote or create_autospec(app.main.UpvoteService, spec_set=True, instance=True),
        'downvote': downvote or create_autospec(app.main.DownvoteService, spec_set=True, instance=True),
        'bookmark': bookmark or create_autospec(app.main.BookmarkService, spec_set=True, instance=True)
    }


def flask_test_client(services=None, environment="testing"):
    application = create_app(services or services_for_test(), environment)
    # If you try to perform database operations outside an application context, you get an error
    application.app_context().push()
    return application.test_client()


def register_mock_mailgun(requests_mock):
    requests_mock.post(MAILGUN_URL, text='resp')


def register_mock_iex(requests_mock):
    # Register mock responses you want returned
    requests_mock.get(IEX_URL + '/AAPL/quote', json=aapl_quote)
    requests_mock.get(IEX_URL + '/AAPL/company', json=aapl_company)
    requests_mock.get(IEX_URL + '/AAPL/chart', json=aapl_chart)
    requests_mock.get(IEX_URL + '/AAPL/advanced-stats', json=aapl_advanced_stats)

    requests_mock.get(IEX_URL + '/GM/quote', json=gm_quote)
    requests_mock.get(IEX_URL + '/GM/company', json=gm_company)
    requests_mock.get(IEX_URL + '/GM/chart', json=gm_chart)
    requests_mock.get(IEX_URL + '/GM/advanced-stats', json=gm_advanced_stats)


def register_mock_alpha_advantage(requests_mock):
    requests_mock.get(ALPHA_ADVANTAGE_URL + '&keywords=AAPL', json=aapl_alpha_advantage)
    requests_mock.get(ALPHA_ADVANTAGE_URL + '&keywords=GM', json=gm_alpha_advantage)
