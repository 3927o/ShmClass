from time import time
from app.extensions import scheduler, db
from app.modules import Task
from app.sms.mail import send_task_remind_mail


def task_remind_job():
    time_now = time()
    time_excess = time_now + 6*60*60
    with scheduler.app.app_context():
        tasks = Task.query.filter(Task.time_end < 30 + time_excess, Task.time_end > -30 + time_excess).all()
        for task in tasks:
            send_task_remind_mail(task)


scheduler.add_job("task_remind", task_remind_job, trigger="interval", minutes=1)
