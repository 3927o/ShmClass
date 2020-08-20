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

    api.add_resource(CurrentTeacherInfoAPI, '/info')
    api.add_resource(TeacherCourseListAPI, '/info/courses', endpoint="courses")
    api.add_resource(TeacherTaskListAPI, '/info/tasks', endpoint="tasks")
    api.add_resource(TeacherInfoAPI, '/<int:uid>/info', endpoint="info")
    api.add_resource(TeacherCertificateAPI, '/certificate', endpoint="certificate")
    api.add_resource(CertificateStatusAPI, '/certificate/status')