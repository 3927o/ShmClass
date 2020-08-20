from flask import Blueprint
from flask_restful import Api

from .resource import TeacherInfoAPI, TeacherCourseListAPI, TeacherTaskListAPI, CurrentTeacherInfoAPI, \
    TeacherCertificateAPI, CertificateStatusAPI


def create_teacher_bp(name="teacher_bp"):

    teacher_bp = Blueprint(name, __name__)

    register_api(teacher_bp)

    return teacher_bp


def register_api(app):
    api = Api(app)

    api.add_resource(CurrentTeacherInfoAPI, '/teacher/info')
    api.add_resource(TeacherCourseListAPI, '/teacher/courses', endpoint="courses")
    api.add_resource(TeacherTaskListAPI, '/teacher/tasks', endpoint="tasks")
    api.add_resource(TeacherInfoAPI, '/teacher/<int:tid>/info', endpoint="info")
    api.add_resource(TeacherCertificateAPI, '/teacher/info/certificate', endpoint="certificate")
    api.add_resource(CertificateStatusAPI, '/teacher/certificate/status')