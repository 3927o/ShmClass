from flask import Blueprint
from flask_restful import Api

from .resources import ImportStudentAPI, ImportTeacherAPI, CourseImportStuAPI


def create_admin_bp(name="admin_bp"):
    admin_bp = Blueprint(name, __name__)

    register_api(admin_bp)

    return admin_bp


def register_api(app):
    api = Api(app)

    api.add_resource(ImportTeacherAPI, "/import/teacher")
    api.add_resource(ImportStudentAPI, "/import/student")
    api.add_resource(CourseImportStuAPI, "/import/student/<int:cid>")

    return api
