import random
from flask_mail import Message

from app.extensions import mail, celery

from app.sms.templates import verify_code_t


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