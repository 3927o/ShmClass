import redis
import pickle
from flask import g

from app.modules import Course
from app.helpers import api_abort
from app.extensions import pool, db


r = redis.Redis(connection_pool=pool)


def get_certificate_info(role, school, role_id):
    key = "certificate:{}:{}:{}".format(role, school, role_id)
    certificate_info = r.get(key)
    if certificate_info is not None:
        # return api_abort(4013, "certificate info do not exit")
        certificate_info = pickle.loads(certificate_info)
    return certificate_info


def validate_certificate_code(certificate_info, code):
    real_code = certificate_info['certificate_code']
    # return api_abort(4014, "wrong certificate_code")
    return code == real_code


def update_user_info(certificate_info):
    user = g.current_user.user
    for item, value in certificate_info.items():
        setattr(user, item, value)


def update_student_course(school, student_id):
    student = g.current_user
    key_courses = "certificate:student:{}:{}:courses".format(school, student_id)
    courses = r.get(key_courses)
    courses = pickle.loads(courses) if courses is not None else []
    for course_id in courses:
        course = Course.query.get(course_id)
        course.students.append(student)


def certificate_user(role, data):
    status = 1
    status_message = "succeed"
    school = data['school']
    role_id = data['role_id']
    code = data['code']

    certificate_info = get_certificate_info(role, school, role_id)
    if certificate_info is None:
        status = 0
        status_message = api_abort(4013, "certificate info do not exit")

    if not validate_certificate_code(certificate_info, code):
        status = 0
        status_message = api_abort(4014, "wrong certificate_code")

    update_user_info(certificate_info)

    if role is "student":
        update_student_course(school, role_id)

    db.session.commit()

    return status, status_message
