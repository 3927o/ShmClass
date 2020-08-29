import redis
import pickle
from flask import request, g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.interceptors import admin_required, resource_found_required
from app.helpers import parse_excel, make_resp
from app.extensions import pool
from app.modules import Student


import_info_reqparser = RequestParser()
import_info_reqparser.add_argument("school", required=True)


r = redis.Redis(connection_pool=pool)


class ImportTeacherAPI(Resource):
    # url: /import/teacher
    # school | teacher_id | name | certificate_code
    method_decorators = [admin_required]

    def post(self):
        school = import_info_reqparser.parse_args()['school']
        teachers = parse_excel(request, "teachers")

        for teacher in teachers:
            if teacher["school"] != school:
                continue

            redis_key = "certificate:teacher:{}:{}".format(teacher["school"], teacher["teacher_id"])
            data = pickle.dumps(teacher)
            r.set(redis_key, data)

        return make_resp(teachers)


class ImportStudentAPI(Resource):
    # url: /import/student
    # excel columns
    # school | student_id | name | certificate_code | grade | class
    method_decorators = [admin_required]

    def post(self):
        school = import_info_reqparser.parse_args()['school']
        students = parse_excel(request, "students")

        for student in students:
            if student["school"] != school:
                continue

            redis_key = "certificate:student:{}:{}".format(student["school"], student["student_id"])
            data = pickle.dumps(student)
            r.set(redis_key, data)

        return make_resp(students)


class CourseImportStuAPI(Resource):
    # url: /import/student/<int:cid>
    # excel columns
    # student_id |
    # can only import student in the school of the course
    method_decorators = [resource_found_required("course"), admin_required]

    def post(self, cid):
        school = g.current_course.teacher.user.school
        data = parse_excel(request, "excel")  # a list of every row data
        stu_id_list = list()
        for item in data:
            stu_id_list.append(item["student_id"])

        for stu_id in stu_id_list:
            student = Student.query.filter_by(student_id=stu_id).first()
            if student is not None and student.user.school == school:
                student.courses.append(g.current_course)
            else:
                redis_key = "certificate:student:{}:{}:courses".format(school, stu_id)
                r.sadd(redis_key, g.current_course.id)

        return make_resp(stu_id_list)


