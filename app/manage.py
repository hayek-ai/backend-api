import os
import unittest

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from main import create_app, db
from application import create_services

config_name = os.environ['APP_SETTINGS']
app = create_app(create_services(), config_name)

app.app_context().push()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def run():
    app.run()


if __name__ == '__main__':
    manager.run()
