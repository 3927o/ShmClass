from flask import Blueprint
from flask_restful import Api

from .resource import StudentCertificateAPI, StudentCourseListAPI, StudentInfoAPI, StudentTaskListAPI, \
    CurrentStudentInfoAPI


def create_student_bp(name="student_bp"):

    student_bp = Blueprint(name, __name__)

    register_api(student_bp)

    return student_bp


def register_api(app):
    api = Api(app)

    api.add_resource(StudentInfoAPI, "/<int:uid>/info", endpoint="info")
    api.add_resource(CurrentStudentInfoAPI, "/info")
    api.add_resource(StudentTaskListAPI, '/info/tasks', endpoint="tasks")
    api.add_resource(StudentCourseListAPI, '/info/course', endpoint="courses")
    api.add_resource(StudentCertificateAPI, "/certificate", endpoint="certificate")

    return api