from flask import Blueprint
from flask_mail import Message

from app.extensions import mail


def create_test_bp(name="test_bp"):
    test_bp = Blueprint(name, __name__)

    def index():
        msg = Message("Hello 3927!", recipients=["1624497311@qq.com", "2900303329@qq.com"], body="body")
        mail.send(msg)
        return "test_cli"
    test_bp.add_url_rule('/', view_func=index)

    return test_bp


def register_blueprints(app):
    pass