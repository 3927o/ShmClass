from flask import g, request
from flask_restful import Resource

from app.interceptors import resource_found_required, login_required_as_teacher, role_required, \
    login_required, login_required_as_student
from app.helpers import make_resp, api_abort, edit_module
from app.modules import Course, Media, Student, page_to_json
from app.extensions import db
from ..reqparsers import course_create_reqparser, course_put_reqparser


class CourseInfoAPI(Resource):
    # url: /course/<int:cid>
    method_decorators = {
        "get": [login_required(allowed_anonymous=True), resource_found_required("course")],
        "put": [role_required("teacher", "course"), resource_found_required("course")],
        "delete": [role_required("teacher", "course"), resource_found_required("course")]
    }

    def get(self, cid):
        resp = g.current_course.to_json(detail=True)
        return make_resp(resp)

    def put(self, cid):
        data = course_put_reqparser.parse_args()
        edit_module(g.current_course, data)
        db.session.commit()

        resp = g.current_course.to_json_as_teacher()
        return make_resp(resp)

    def delete(self, cid):
        db.session.delete(g.current_course)
        db.session.commit()
        return make_resp("OK")


class CourseListAPI(Resource):
    # url: /course/course_list

    @login_required(allowed_anonymous=True)
    def get(self):
        courses = Course.query.filter_by(public=True).all()
        resp = page_to_json(Course, courses, type_="course")
        return make_resp(resp)

    @login_required_as_teacher
    def post(self):
        data = course_create_reqparser.parse_args()
        new_course = Course(data['name'], data['public'], g.current_user.tid,
                            data['start_at'], data['end_at'], data['introduce'])

        avatar = request.files.get("avatar")
        if avatar is None:
            return api_abort(4001, "file avatar missing")
        avatar_uuid = Media.save_media(avatar, "avatars/course", commit=False)
        new_course.avatar = avatar_uuid

        db.session.add(new_course)
        db.session.commit()
        return make_resp(new_course.to_json_as_teacher())


class CourseStudentsAPI(Resource):
    # url: /<int:cid>/students
    method_decorators = [role_required("teacher", "course"), resource_found_required("course")]

    def get(self, cid):
        students = g.current_course.students
        resp = page_to_json(Student, students)
        return make_resp(resp)


class JoinCourseAPI(Resource):
    # url: /course/<int:cid>/join
    method_decorators = [login_required_as_student, resource_found_required("course")]

    def post(self, cid):
        if not g.current_course.public:
            return api_abort(4031, "It's not a public course")

        g.current_course.students.append(g.current_user)
        db.session.commit()

        return make_resp("OK")


class LeaveCourseAPI(Resource):
    # url: /course/<int:cid>/leave
    method_decorators = [login_required_as_student, resource_found_required("course")]

    def post(self, cid):
        if g.current_user in g.current_course.students:
            g.current_course.students.remove(g.current_user)

        return make_resp("OK")


url_prefix = ""


def register_recourse_course(api):
    api.add_resource(CourseInfoAPI, url_prefix + "/<int:cid>", endpoint="course")
    api.add_resource(CourseListAPI, url_prefix + "/course_list", endpoint="courses")
    api.add_resource(CourseStudentsAPI, url_prefix + "/<int:cid>/students")
    api.add_resource(JoinCourseAPI, url_prefix + "/<int:cid>/join")
    api.add_resource(LeaveCourseAPI, url_prefix + "/<int:cid>/leave")
