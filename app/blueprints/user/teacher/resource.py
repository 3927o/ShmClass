import pickle
import redis
from flask import g
from flask_restful import Resource

from app.helpers import make_resp
from app.interceptors import resource_found_required, login_required_as_teacher as login_required
from app.modules import Course, Task, User
from app.extensions import pool, db
from app.blueprints.user.helpers import certificate_user

from .reqparsers import teacher_put_reqparser, teacher_certificate_reqparser


r = redis.Redis(connection_pool=pool)


class TeacherInfoAPI(Resource):
    # url: /teacher/<int:uid>/info
    method_decorators = [resource_found_required("user")]

    def get(self, uid):
        resp = g.current_user.teacher.to_json()
        return make_resp(resp)


class CurrentTeacherInfoAPI(Resource):
    # url: /teacher/info
    method_decorators = [login_required]

    def get(self):
        resp = g.current_user.to_json(detail=True)
        return make_resp(resp)

    def put(self):
        teacher = g.current_user.user
        put_data = teacher_put_reqparser.parse_args()

        for item, value in put_data.items():
            setattr(teacher, item, value)
        db.session.commit()

        resp = g.current_user.to_json(detail=True)
        return make_resp(resp)


class TeacherCourseListAPI(Resource):
    # url: /teacher/info/courses
    method_decorators = [login_required]

    def get(self):
        courses = g.current_user.courses
        resp = Course.list_to_json(courses, "teacher")
        return make_resp(resp)


class TeacherTaskListAPI(Resource):
    # url: /teacher/info/tasks
    method_decorators = [login_required]

    def get(self):
        tasks = g.current_user.tasks
        resp = Task.list_to_json(tasks, "teacher")
        return make_resp(resp)


class TeacherCertificateAPI(Resource):
    # url: /teacher/info/certificate
    method_decorators = [login_required]

    def post(self):
        data = teacher_certificate_reqparser.parse_args()

        status, wrong_message = certificate_user("teacher", data)

        if status:
            g.current_user.certificated = True
            return make_resp("OK")
        else:
            return wrong_message


class CertificateStatusAPI(Resource):
    # url: /teacher/certificate/status
    method_decorators = [login_required]

    def get(self):
        return make_resp(int(g.current_user.certificated))