import redis
import pickle
from flask import g
from flask_restful import Resource

from app.interceptors import login_required_as_student as login_required
from app.helpers import make_resp, api_abort
from app.modules import Course, Task
from app.extensions import pool, db
from app.blueprints.user.helpers import certificate_user

from .reqparsers import student_put_reqparser, stu_certificate_reqparser


r = redis.Redis(connection_pool=pool)


class StudentInfoAPI(Resource):
    # url: /student/<int:sid>/info
    method_decorators = [login_required]

    def get(self):
        resp = g.current_user.to_json()
        return make_resp(resp)


class CurrentStudentInfoAPI(Resource):
    method_decorators = [login_required]

    def get(self):
        resp = g.current_user.to_json(detail=True)
        return make_resp(resp)

    def put(self):
        student = g.cuurent_user.user
        put_data = student_put_reqparser.parse_args()

        for item, value in put_data.items():
            setattr(student, item, value)
        db.session.commit()

        resp = g.current_user.to_json(detail=True)
        return make_resp(resp)


class StudentCourseListAPI(Resource):
    method_decorators = [login_required]

    def get(self):
        courses = g.current_user.courses
        resp = Course.list_to_json(courses, "student")
        return make_resp(resp)


class StudentTaskListAPI(Resource):
    method_decorators = [login_required]

    def get(self):
        tasks = g.current_user.tasks
        resp = Task.list_to_json(tasks, "student")
        return make_resp(resp)


class StudentCertificateAPI(Resource):
    # url: /student/info/certificate
    method_decorators = [login_required]

    def post(self):
        data = stu_certificate_reqparser.parse_args()

        status, wrong_message = certificate_user("student", data)

        if status:
            return make_resp("OK")
        else:
            return wrong_message
