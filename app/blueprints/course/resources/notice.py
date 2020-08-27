# encoding:utf-8
import redis
import pickle
from flask import g, request
from flask_restful import Resource

from app.interceptors import resource_found_required, role_required
from app.helpers import make_resp, api_abort
from app.extensions import db, pool
from app.modules import Notice, Commit, page_to_json
from app.sms.mail import send_tips_mail

from ..reqparsers import notice_create_reqparser, commit_create_reqparser


r = redis.Redis(connection_pool=pool)


class NoticeAPI(Resource):
    # url: /course/<int:cid>/notices/<string:notice_id>
    method_decorators = {"get": [role_required("student", "notice"), resource_found_required("notice")],
                         "post": [role_required("student", "notice"), resource_found_required("notice")],
                         "delete": [role_required("teacher", "notice"), resource_found_required("notice")]}

    def get(self, cid, notice_id):
        resp = g.current_notice.to_json(detail=True)
        return make_resp(resp)

    def post(self, cid, notice_id):
        key_notice_read = "notice:read:{}".format(notice_id)
        key_user_cnt = "notice:read:cid:{}:uid:{}".format(cid, g.current_user.id)
        r.sadd(key_notice_read, g.current_user.id)
        r.incr(key_user_cnt)
        return make_resp("OK")

    def delete(self, cid, notice_id):
        db.session.delete(g.current_notice)
        db.session.commit()
        return make_resp("OK")


class NoticeListAPI(Resource):
    # url: /course/<int:id>/notices
    method_decorators = {"get": [role_required("student"), resource_found_required("course")],
                         "post": [role_required("teacher"), resource_found_required("course")]}

    def get(self, cid):
        notices = g.current_course.notices
        resp = page_to_json(Notice, notices)
        return make_resp(resp)

    def post(self, cid):
        data = notice_create_reqparser.parse_args()
        new_notice = Notice(data['title'], data['content'])
        new_notice.course = g.current_course

        send_tips_mail(g.current_course, "通知")

        db.session.add(new_notice)
        db.session.commit()
        resp = new_notice.to_json(detail=True)
        return make_resp(resp)


class CommitAPI(Resource):
    # url: /course/<int:cid>/commit
    method_decorators = {"get": [role_required("student"), resource_found_required("course")],
                         "post": [role_required("teacher"), resource_found_required("course")],
                         "put": [role_required("student"), resource_found_required("course")]}

    def get(self, cid):
        # get commit status and it's info
        current_commit = Commit.get_current_commit(g.current_course)
        if current_commit is None:
            resp = {"exist": 0}
        else:
            resp = current_commit.json()
            resp['exist'] = 1
            resp['finish'] = int(g.current_user.name in current_commit.finished)

        return make_resp(resp)

    def post(self, cid):
        # submit a commit
        data = commit_create_reqparser.parse_args()
        status, message = Commit.validate_commit_time(g.current_course.id, data['expires'] * 60)
        if not status:
            return api_abort(4004, message)

        new_commit = Commit(g.current_course, data['expires'] * 60)
        send_tips_mail(g.current_course, "签到")
        return make_resp(new_commit.json())

    def put(self, cid):
        # make a commit
        current_commit = Commit.get_current_commit(g.current_course)
        if current_commit is None:
            return api_abort(400, "there do not exist commit now")

        if g.current_user.name in current_commit.finished:
            return api_abort(4005, "you already finished the commit")

        current_commit.make_commit(g.current_user)
        r.lset("commits:{}".format(g.current_course.id), 0, pickle.dumps(current_commit))

        return make_resp("OK")


class CommitStatisticsAPI(Resource):
    # url: /course/<int:cid>/commit/statistics?commit_id=
    method_decorators = [role_required("teacher"), resource_found_required("course")]

    def get(self, cid):
        commits = Commit.get_commits(g.current_course)

        # find commit by commit id
        commit_id = request.args.get("commit_id")
        if commit_id is not None:
            status = 0
            for commit in commits:
                if commit['id'] == commit_id:
                    commits = [commit]
                    status = 1
                    break
            if not status:
                return api_abort(4043, "resource commit not found")

        resp = page_to_json(Commit, commits, statistic=True)
        return make_resp(resp)


def register_recourse_notice(api):
    api.add_resource(NoticeAPI, "/<int:cid>/notices/<string:notice_id>", endpoint="notice")
    api.add_resource(NoticeListAPI, "/<int:cid>/notices", endpoint="notices")
    api.add_resource(CommitAPI, "/<int:cid>/commit", endpoint="statistic")
    api.add_resource(CommitStatisticsAPI, "/<int:cid>/commit/statistics")
