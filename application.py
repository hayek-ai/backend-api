import os
from app.main import create_app
from app.main.service.user_service import UserService


def create_services():
    services = {"user": UserService()}
    return services


config_name = os.getenv('APP_SETTINGS')
app = create_app(create_services(), config_name)

if __name__ == '__main__':
    app.run()
