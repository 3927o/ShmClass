import random
import redis
from flask import current_app, g, request
from flask_restful import Resource

from app.modules import User
from app.helpers import api_abort, validate_verify_code, make_resp
from app.extensions import db, pool
from app.sms.mail import send_verify_code_mail
from app.interceptors import login_required

from .reqparsers import signup_reqparser, verify_code_reqparser, login_reqparser, pwd_login_reqparser, \
    tel_login_reqparser, user_del_reqparser, reset_pwd_reqparser, reset_email_reqparser
from .schemas import user_schema_signup
from .helpers import get_user_by_name_tel_mail, generate_token_info


r = redis.Redis(connection_pool=pool)


class LoginAPI(Resource):
    # url: /login?method=[0, 1]
    def post(self):
        reqparser = [pwd_login_reqparser, tel_login_reqparser]
        auth_user_funcs = [auth_user_by_pwd, auth_user_by_phone]

        data = login_reqparser.parse_args()
        method = data['method']

        data = reqparser[method].parse_args()
        user, message = auth_user_funcs[method](data)
        g.current_user = user

        if message is not 'succeed' or user is None:
            return api_abort(4012, message)

        token_info = generate_token_info(user)
        resp = user_schema_signup(user)
        resp.update(token_info)

        return make_resp(resp)


class SignupAPI(Resource):
    def post(self):
        data = signup_reqparser.parse_args()

        if not validate_verify_code(0, data['code'], data['email']):
            return api_abort(4011, "Wrong Verify Code.")

        new_user = User(data['nickname'], data['email'], data['password'])
        db.session.add(new_user)
        db.session.commit()

        resp = user_schema_signup(new_user)
        return make_resp(resp)


class AccountDelAPI(Resource):
    # url: /account/del
    method_decorators = [login_required]

    def delete(self):
        code = user_del_reqparser.parse_args()["verify_code"]

        if not validate_verify_code(4, code, g.current_user.email):
            return api_abort(4011, "Wrong Verify Code.")

        db.session.delete(g.current_user)
        db.session.commit()
        return make_resp("OK")


class ResetPwdAPI(Resource):
    # url: /account/pwd/reset
    method_decorators = [login_required]

    def post(self):
        data = reset_pwd_reqparser.parse_args()
        code = data['verify_code']
        new_pwd = data['new_pwd']

        if not validate_verify_code(3, code, g.current_user.email):
            return api_abort(4011, "Wrong Verify Code.")

        g.current_user.set_password(new_pwd)

        return make_resp("OK")


class ResetEmailAPI(Resource):
    # url: /account/email/reset
    method_decorators = [login_required]

    def post(self):
        data = reset_email_reqparser.parse_args()
        old_code = data['old_email_code']
        new_code = data['new_email_code']
        new_email = data['new_email']

        if not validate_verify_code(2, old_code, g.current_user.email):
            return api_abort(4011, "Wrong Verify Code.")
        if not validate_verify_code(2, new_code, new_email):
            return api_abort(4011, "Wrong Verify Code.")

        setattr(g.current_user, "email", new_email)

        return make_resp("OK")


class VerifyCodeAPI(Resource):
    def post(self):
        # get action and email from request
        data = verify_code_reqparser.parse_args()
        code_type = data["type"]
        action = current_app.config["CODE_TYPE"][code_type]
        email = data['email']

        # generate the code to send. if there cached a code the same type with which going to be send, use it.
        key = "VerifyCode:{}:{}".format(action, email)
        existed_code = r.get(key)
        if not existed_code:
            code = random.randint(100001, 999999)
        else:
            code = existed_code

        # send code and cache it
        send_verify_code_mail(code, email)
        r.set(key, code, ex=60*5, nx=True)

        return make_resp("OK")


class CheckNameExitAPI(Resource):
    # url: /check/nickname?nickname={{name}}
    def get(self):
        nickname = request.args.get('nickname')
        if nickname is None:
            return api_abort(4000, "param nickname missing")
        user = User.query.filter_by(nickname=nickname).first()
        if user is None:
            exit_status = 0
        else:
            exit_status = 1
        return make_resp(exit_status)


class CheckMailExitAPI(Resource):
    # url: /check/email?email={{email}}
    def get(self):
        email = request.args.get('email')
        if email is None:
            return api_abort(400, "param tel missing")
        user = User.query.filter_by(email=email).first()
        if user is None:
            exit_status = 0
        else:
            exit_status = 1
        return make_resp(exit_status)


def auth_user_by_pwd(data):
    username_or_tel_or_mail = data['username']
    pwd = data['password']
    message = 'succeed'

    user = get_user_by_name_tel_mail(username_or_tel_or_mail)

    if user is None:
        message = 'user do not exist'

    if user is not None and not user.validate_password(pwd):
        message = "wrong password"

    return user, message


def auth_user_by_phone(data):
    mail = data['mail']
    verify_code = data['code']
    message = 'succeed'

    user = User.query.filter_by(email=mail).first()

    if user is None:
        message = 'user do not exit'

    if not validate_verify_code(1, verify_code, mail):
        message = 'wrong verify code'

    return user, message