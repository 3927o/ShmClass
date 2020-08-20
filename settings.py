import os
import sys
from flask import json
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig:

    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(16))

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CODE_TYPE = ['SignUp', 'LogIn', 'ChangeMail', 'ChangePassword', 'DelAccount']
    SELECT_TYPE = ['select', 'mselect', 'judge']
    TEMPLATE_CODE = {"verify": "SMS_186947418", "notice": "SMS_193510835"}

    ACCESS_TOKEN_EXPIRES = 3600 * 24 * 7
    REFRESH_TOKEN_EXPIRES = 3600 * 24 * 30
    KEY_ACCESS_TOKEN = "token:access"
    KEY_REFRESH_TOKEN = "token:refresh"

    MAIL_SERVER = "smtp.qq.com"
    MAIL_USERNAME = "1624497311@qq.com"
    MAIL_PASSWORD = "zvjmrrnsyvcvbega"
    MAIL_DEFAULT_SENDER = ("水火木课堂", "1624497311@qq.com")
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_PORT = 465

    CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

    SCHEDULER_API_ENABLED = True


class DevelopmentConfig(BaseConfig):
    SECRET_KEY = os.getenv('SECRET_KEY', "secret_key")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1/test'
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = os.getenv('SECRET_KEY', "secret_key")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1/test'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}