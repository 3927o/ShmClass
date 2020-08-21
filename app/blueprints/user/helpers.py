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
    role = g.current_user
    user = role.user
    for item, value in certificate_info.items():
        if hasattr(user, item):
            setattr(user, item, value)
        else:
            setattr(role, item, value)


def update_student_course(school, student_id):
    student = g.current_user
    key_courses = "certificate:student:{}:{}:courses".format(school, student_id)

    courses = r.smembers(key_courses)
    if not courses:
        courses = set()

    for course_id in courses:
        course_id = int(course_id)
        course = Course.query.get(course_id)
        course.students.append(student)

    r.delete(key_courses)


def certificate_user(role, data):
    status = 1
    status_message = "succeed"
    school = data['school']
    role_id = data['role_id']
    code = data['certificate_code']

    certificate_info = get_certificate_info(role, school, role_id)
    if certificate_info is None:
        status = 0
        status_message = api_abort(4013, "certificate info do not exit")
        return status, status_message

    if not validate_certificate_code(certificate_info, code):
        status = 0
        status_message = api_abort(4014, "wrong certificate_code")
        return status, status_message

    update_user_info(certificate_info)

    if role is "student":
        update_student_course(school, role_id)

    r.delete("certificate:{}:{}:{}".format(role, school, role_id))
    db.session.commit()

    return status, status_message
