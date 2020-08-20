import redis
from time import time
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

from flask import request, current_app

from app.modules import User
from app.extensions import pool

from settings import config


r = redis.Redis(connection_pool=pool)

config = config["production"]
key_access_token = config.KEY_ACCESS_TOKEN
key_refresh_token = config.KEY_REFRESH_TOKEN
access_token_expires = config.ACCESS_TOKEN_EXPIRES
refresh_token_expires = config.REFRESH_TOKEN_EXPIRES


def get_token():
    token = request.headers.get('Authorization', None)

    if token is None:
        return None, None

    try:
        access_token = token.split(';')[0]
        refresh_token = token.split(';')[1]
    except IndexError:
        access_token = token.split(';')[0]
        refresh_token = None

    return access_token, refresh_token


def generate_token(user, token_type, expires=3600 * 24 * 7, json_user=False):
    # generate token with user's info
    s = Serializer(current_app.secret_key, expires_in=expires)

    if json_user:
        data = user
    else:
        data = user.to_json(detail=True)
    data['token_type'] = token_type

    token = s.dumps(data).decode('ascii')
    time_expires = time() + expires

    key = "token" + ':' + token_type
    r.zadd(key, {token: time_expires})

    return token


def load_token(token):
    # read user's info from token
    # return: dict

    # use for testing. while the token is integer, return the corresponding user.
    if isinstance(token, int):
        user = User.query.get(token)
        return user

    s = Serializer(current_app.secret_key)

    try:
        user_data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return None

    uid = user_data['uid']
    user = User.query.get(uid)

    return user


def generate_token_info(user):

    access_token = generate_token(user, 'access', access_token_expires)
    refresh_token = generate_token(user, 'refresh', refresh_token_expires)
    token_info = {"access_token": access_token,
                  "refresh_token": refresh_token,
                  "expires_access": access_token_expires,
                  "expires_refresh": refresh_token_expires}

    return token_info


def zismember(key, value):
    sorted_set = r.zrangebyscore(key, time(), 10000000000)
    return value in sorted_set


def get_user_by_name_tel_mail(name_tel_mail):
    user = User.query.filter_by(nickname=name_tel_mail).first()
    if user is None:
        user = User.query.filter_by(telephone=name_tel_mail).first()
    if user is None:
        user = User.query.filter_by(email=name_tel_mail).first()

    return user