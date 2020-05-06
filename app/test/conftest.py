from unittest.mock import create_autospec
from app.main import create_app
import app


def services_for_test(user=None, confirmation=None, idea=None):
    return {
        'user': user or create_autospec(app.main.UserService, spec_set=True, instance=True),
        'confirmation': confirmation or create_autospec(app.main.ConfirmationService, spec_set=True, instance=True),
        'idea': idea or create_autospec(app.main.IdeaService, spec_set=True, instance=True)
    }


def flask_test_client(services=None, environment="testing"):
    application = create_app(services or services_for_test(), environment)
    # If you try to perform database operations outside an application context, you get an error
    application.app_context().push()
    return application.test_client()

