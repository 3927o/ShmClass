from flask import Blueprint
from flask_restful import Api

from .resources import register_resources


def create_course_bp(name="course_bp"):

    course_bp = Blueprint(name, __name__)

    register_api(course_bp)

    return course_bp


def register_api(app):
    api = Api(app)
    register_resources(api)
    return api
