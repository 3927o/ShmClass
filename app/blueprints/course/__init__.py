from flask import Blueprint


def create_course_bp(name="course_bp"):

    course_bp = Blueprint(name, __name__)

    return course_bp