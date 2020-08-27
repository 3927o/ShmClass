from flask import current_app
from time import time
from app.extensions import scheduler
from app.modules import Task, Course
from app.sms.mail import send_task_remind_mail, send_course_end_notice_mail


def task_remind_job():
    time_now = time()
    time_excess = time_now + 6*60*60
    with scheduler.app.app_context():
        tasks = Task.query.filter(Task.time_end < 30 + time_excess, Task.time_end > -30 + time_excess).all()
        current_app.logger.debug(str(len(tasks)))
        for task in tasks:
            send_task_remind_mail(task)


def course_end_tips_job():
    time_now = time()
    time_notice = time_now + 24*60*60
    with scheduler.app.app_context():
        courses = Course.query.filter(Course.end_at > time_notice - 30, Course.end_at < time_notice + 30).all()
        print("courses:" + str(len(courses)))
        for course in courses:
            send_course_end_notice_mail(course)


scheduler.add_job("task_remind", task_remind_job, trigger="interval", seconds=60)
scheduler.add_job("course_end_tips", course_end_tips_job, trigger="interval", seconds=60)
