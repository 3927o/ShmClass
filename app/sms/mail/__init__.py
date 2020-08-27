import random
from flask_mail import Message

from app.extensions import mail, celery

from app.sms.templates import verify_code_t, course_tips_t, task_remind_t, course_end_tips_t


def send_mail(template, recipients):
    if isinstance(recipients, str):
        recipients = [recipients]

    msg = Message(template.subject, body=template.body, recipients=recipients)
    mail.send(msg)


def send_verify_code_mail(code, recipients):
    if code is None:
        code = random.randint(100001, 999999)

    template = verify_code_t()
    template.format(code)

    send_mail(template, recipients)


def send_tips_mail(course, resource_type):
    recipients = []

    template = course_tips_t()
    template.format(course.name, resource_type)

    for student in course.students:
        recipients.append(student.user.email)

    if recipients:
        send_mail(template, recipients)


def send_task_remind_mail(task):
    recipients = []

    template = task_remind_t()
    template.format(task.course.name)

    for student in task.students:
        if not task.finished(student.user):
            recipients.append(student.user.email)

    if recipients:
        send_mail(template, recipients)


def send_course_end_notice_mail(course):
    recipients = []

    template = course_end_tips_t()
    template.format(course.name)

    for student in course.students:
        recipients.append(student.user.email)
    print("recipients:" + str(len(recipients)))
    if recipients:
        send_mail(template, recipients)
