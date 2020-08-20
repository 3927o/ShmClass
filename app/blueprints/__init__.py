from .auth import create_auth_bp
from .user import create_student_bp
from .user import create_teacher_bp
from .course import create_course_bp
from .test import create_test_bp
from .admin import create_admin_bp


auth_bp = create_auth_bp()
student_bp = create_student_bp()
teacher_bp = create_teacher_bp()
course_bp = create_course_bp()
test_bp = create_test_bp()
admin_bp = create_admin_bp()


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(teacher_bp, url_prefix="/api/teacher")
    app.register_blueprint(course_bp, url_prefix="/api/course")
    app.register_blueprint(test_bp, url_prefix="/api/test")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
