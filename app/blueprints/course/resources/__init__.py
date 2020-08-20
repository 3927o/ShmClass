from .course import register_recourse_course
from .document import register_recourse_document
from .discussion import register_recourse_discussion
from .movie import register_recourse_movie
from .notice import register_recourse_notice
from .task import register_recourse_task


def register_resources(api):
    register_recourse_notice(api)
    register_recourse_task(api)
    register_recourse_movie(api)
    register_recourse_discussion(api)
    register_recourse_document(api)
    register_recourse_course(api)
