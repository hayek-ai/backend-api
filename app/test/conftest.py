from unittest.mock import create_autospec
from app.main import create_app
import app


def services_for_test(register_user=None):
    return {'register_user': register_user or create_autospec(app.main.RegisterUserService, spec_set=True, instance=True)}


def flask_test_client(services=None, environment="testing"):
    app = create_app(services or services_for_test(), environment)
    return app.test_client()

