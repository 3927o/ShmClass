import redis

from flask import request, g

from app.extensions import pool, db
from app.helpers import api_abort, get_current_course
from app.modules import User, Discussion, Course, Task, Problem, TaskAnswer, Chapter, Comment, Notice, Media
from app.blueprints.auth.helpers import get_token, load_token, zismember, generate_token_info
from settings import BaseConfig


r = redis.Redis(connection_pool=pool)

key_access_token = BaseConfig.KEY_ACCESS_TOKEN
key_refresh_token = BaseConfig.KEY_REFRESH_TOKEN
access_token_expires = BaseConfig.ACCESS_TOKEN_EXPIRES
refresh_token_expires = BaseConfig.REFRESH_TOKEN_EXPIRES


def auth_required(allowed_anonymous=False):

    def wrapper(f):
        # no need of user info, auth only

        def decorator(*args, **kws):

            # search access token
            access_token, refresh_token = get_token()
            if access_token is None:
                if allowed_anonymous:
                    access_token, refresh_token = 0, 0
                else:
                    return api_abort(4010, "access token is required")

            # use for testing. while the access token is integer, it stands for a user whose id is it.
            try:
                access_token = int(access_token)
                g.current_token = access_token
                resp = f(*args, **kws)
                return resp
            except (ValueError, TypeError):
                pass

            # validate access token and go on request
            if zismember(key_access_token, access_token):
                g.current_token = key_access_token
                resp = f(*args, **kws)
                return resp

            # search refresh token
            if refresh_token is None:
                return api_abort(4010, "bad access token, refresh token is required")

            # validate refresh token, refresh it and go on request
            if zismember(key_refresh_token, refresh_token):
                user = load_token(refresh_token)
                if user is None:
                    return api_abort(4010, "Bad Token")

                # refresh token and get new token info
                r.srem(key_refresh_token, refresh_token)  # remove old refresh token from redis db
                token_info = generate_token_info(user)
                g.current_token = token_info["access_token"]

                # go on response
                resp = f(*args, **kws)
                resp.update(token_info)
                return resp

            return f(*args, **kws)

        return decorator

    return wrapper


def login_required(allowed_anonymous=False):

    def wrapper(f):
        # user info will be loaded into g.current_user

        @auth_required(allowed_anonymous=allowed_anonymous)
        def decorator(*args, **kws):
            current_user = load_token(g.current_token)

            # just an insurance
            if current_user is None:
                if not allowed_anonymous:
                    return api_abort(4010, "Bad Token")
                else:
                    current_user = User("anonymous", "anonymous@anonymous.com", "anonymous")

            g.current_user = current_user
            resp = f(*args, **kws)
            return resp

        return decorator

    return wrapper


def login_required_as_teacher(f):
    @login_required()
    def decorator(*args, **kws):
        g.current_user = g.current_user.teacher

        if not g.current_user.certificated:
            return api_abort(4031, "teacher have not certificated")

        resp = f(*args, **kws)
        return resp
    return decorator


def login_required_as_student(f):
    @login_required()
    def decorator(*args, **kws):
        g.current_user = g.current_user.student
        resp = f(*args, **kws)
        return resp
    return decorator


def resource_found_required(resource_name):
    def wrapper(f):

        def decorator(*args, **kws):
            resource_name_module_map = {"user": User, "course": Course, "task": Task, "discussion": Discussion,
                                        "chapter": Chapter, "problem": Problem, "task_answer": TaskAnswer,
                                        "comment": Comment, "notice": Notice, "media": Media}
            module = resource_name_module_map[resource_name]

            resource_id = find_resource_id(module.id_name)
            if resource_id is None:
                return api_abort(4000, "{} id is required".format(resource_name))

            resource = module.query.get(resource_id)
            if resource is None:
                return api_abort(4040, "resource {} not found".format(resource_name))

            setattr(g, "current_"+resource_name, resource)

            return f(*args, **kws)
        return decorator

    return wrapper


def role_required(role, resource_name="course"):

    def wrappers(f):

        @login_required()
        def decorator(*args, **kws):
            user = g.current_user
            course = get_current_course(resource_name)

            if course is None:
                return api_abort(4041, "resource's course not found")

            real_role = user.judge_role(course)
            if role != real_role and not (role == "student" and real_role == "teacher"):
                return api_abort(4030, "you are not the {}".format(role))

            resp = f(*args, **kws)
            return resp
        return decorator

    return wrappers


def admin_required(f):
    @login_required()
    def decorator(*args, **kws):
        if not g.current_user.admin:
            return api_abort(4031, "Admin Required")
        resp = f(*args, **kws)
        return resp
    return decorator


def find_resource_id(id_name):
    resource_id = request.view_args.get(id_name, None)
    if resource_id is None:
        resource_id = request.values.get(id_name, None)
    return resource_id
