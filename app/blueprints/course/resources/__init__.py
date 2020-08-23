from .course import register_recourse_course
from .discussion import register_recourse_discussion
from .media import register_recourse_media
from .notice import register_recourse_notice
from .task import register_recourse_task


def register_resources(api):
    register_recourse_notice(api)
    register_recourse_task(api)
    register_recourse_discussion(api)
    register_recourse_media(api)
    register_recourse_course(api)
