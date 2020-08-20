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

    api.add_resource(StudentInfoAPI, "/student/<int:sid>/info", endpoint="info")
    api.add_resource(CurrentStudentInfoAPI, "/student/info")
    api.add_resource(StudentTaskListAPI, '/student/info/tasks', endpoint="tasks")
    api.add_resource(StudentCourseListAPI, '/student/info/course', endpoint="courses")
    api.add_resource(StudentCertificateAPI, "/student/certificate", endpoint="certificate")

    return api