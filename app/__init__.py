import os
from flask import Flask

from app.helpers import AppDispatcher
from app.blueprints import register_blueprints
from app.extensions import register_extensions

from settings import config


def create_app(config_name=None, **options):
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", 'production')

    # dispatcher = AppDispatcher(__name__, **options)
    # dispatcher.config.from_object(config[config_name])

    app = Flask(__name__, **options)
    app.config.from_object(config[config_name])

    register_blueprints(app)
    register_extensions(app)

    return app


# def register_apps(dispatcher, config_name):
#     teacher_app = create_teacher_app(config_name)
#     student_app = create_student_app(config_name)
#     test_app = create_test_app(config_name)
#     auth_app = create_auth_app(config_name)
#
#     dispatcher.register_app(teacher_app, "/api/teacher")
#     dispatcher.register_app(student_app, "/api/student")
#     dispatcher.register_app(auth_app, "/api/auth")
#     dispatcher.register_app(test_app, "/api/test")
