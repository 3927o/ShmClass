# encoding:utf-8


class Template:
    subject = None
    body = None

    def __init__(self, body, subject=""):
        self.subject = subject
        self.body = body

    def format(self, *args, **kwargs):
        self.body = self.body.format(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.body = self.body.format(*args, **kwargs)

    def __dict__(self):
        return {
            "subject": self.subject,
            "body": self.body
        }


def verify_code_t():
    verify_code_body = "您好，您正在进行身份认证，验证码是{}， 打死也不要告诉别人喔！"
    verify_code_sub = "[水火木课堂]身份验证"
    return Template(verify_code_body, verify_code_sub)


def course_tips_t():
    verify_code_body = "您好，您加入的课程[{}]刚刚发布了新的{}，赶紧进入课堂查看吧！"
    verify_code_sub = "[水火木课堂]课程通知"
    return Template(verify_code_body, verify_code_sub)


def task_remind_t():
    verify_code_body = "您好，您加入的课程[{}]有一门作业即将在6小时后截止，请尽快完成喔。"
    verify_code_sub = "[水火木课堂]作业提醒"
    return Template(verify_code_body, verify_code_sub)
