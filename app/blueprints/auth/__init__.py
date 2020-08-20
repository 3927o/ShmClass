from flask import Blueprint
from flask_restful import Api

from .resources import VerifyCodeAPI, SignupAPI, LoginAPI, CheckNameExitAPI, CheckMailExitAPI, ResetEmailAPI, \
    ResetPwdAPI, AccountDelAPI


def create_auth_bp(name="auth_bp"):

    auth_bp = Blueprint(name, __name__)

    register_api(auth_bp)

    return auth_bp


def register_api(bp):
    api = Api(bp)

    api.add_resource(SignupAPI, '/signup', endpoint='signup')
    api.add_resource(VerifyCodeAPI, '/verify_code')
    api.add_resource(LoginAPI, '/login')
    api.add_resource(CheckMailExitAPI, '/check/mail')
    api.add_resource(CheckNameExitAPI, "/check/nickname")
    api.add_resource(ResetPwdAPI, '/account/pwd/reset')
    api.add_resource(ResetEmailAPI, '/account/email/reset')
    api.add_resource(AccountDelAPI, '/account/del')