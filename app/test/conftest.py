from app.main import create_app


def flask_test_client(environment="testing"):
    app = create_app(environment)
    return app.test_client()

