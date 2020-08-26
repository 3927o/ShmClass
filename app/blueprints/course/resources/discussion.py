import redis
import pickle
from flask import g, request
from flask_restful import Resource

from app.interceptors import resource_found_required, role_required, login_required
from app.helpers import make_resp, api_abort
from app.modules import Discussion, Comment, page_to_json
from app.extensions import db, pool

from ..reqparsers import discussion_create_reqparser, comment_reqparser


r = redis.Redis(connection_pool=pool)


class DiscussionAPI(Resource):
    # url: /course/<int:cid>/discussions/<string:discus_id>
    method_decorators = [role_required("student", "discussion"), resource_found_required("discussion")]

    def get(self, cid, discus_id):
        # get a discussion and its comments
        discussion = g.current_discussion
        return make_resp(discussion.to_json(detail=True))


class DiscussionListAPI(Resource):
    # url: /course/<int:cid>/discussions
    method_decorators = [role_required("student", "course"), resource_found_required("course")]

    def get(self, cid):
        # get discussions
        discussions = g.current_course.discussions
        resp = page_to_json(Discussion, discussions)
        return make_resp(resp)

    def post(self, cid):
        # post a discussion
        data = discussion_create_reqparser.parse_args()
        new_discussion = Discussion(data['content'])
        new_discussion.master = g.current_user
        new_discussion.course = g.current_course
        db.session.add(new_discussion)
        db.session.commit()
        return make_resp(new_discussion.to_json(detail=True))


class CommentListAPI(Resource):
    # url: /course/<int:cid>/discussions/<string:discus_id>/comments
    method_decorators = [role_required("student", "discussion"), resource_found_required("discussion")]

    def get(self, cid, discus_id):
        comments = g.current_discussion.comments
        data = page_to_json(Comment, comments)
        return make_resp(data)

    def post(self, cid, discus_id):
        # post a comment
        data = comment_reqparser.parse_args()
        new_comment = Comment(data['content'], data['reply'])
        new_comment.author = g.current_user
        new_comment.discussion = g.current_discussion
        db.session.add(new_comment)

        if data['reply'] is not None:
            comment_reply = Comment.query.get(data['reply'])
            if comment_reply is None:
                return api_abort(4042, "comment reply is not exist")
            replies = pickle.loads(comment_reply.replies)
            replies.append(new_comment.id)
            comment_reply.replies = pickle.dumps(replies)

        resp = new_comment.to_json()
        db.session.commit()
        return make_resp(resp)


class CommentAPI(Resource):
    # url: /course/<int:cid>/comment/<string:comment_id>
    method_decorators = [role_required("student", "comment"), resource_found_required("comment")]

    def get(self, cid, comment_id):
        resp = g.current_comment.to_json()
        return make_resp(resp)


class CommentLikeAPI(Resource):
    # url: /courses/<int:cid>/comment/<string:comment_id>/like
    method_decorators = [role_required("student", "comment"), resource_found_required("comment")]

    def post(self, cid, comment_id):
        if g.current_user.liked(comment_id, "comment"):
            return api_abort(4003, "already liked this item")
        g.current_user.like(comment_id, "comment")
        return make_resp("OK")


class DiscussionCollectAPI(Resource):
    # url: /courses/<int:cid>/discussions/<string:discuss_id>/collect
    method_decorators = [role_required("student", "discussion"), resource_found_required("discussion")]

    def post(self, cid, discus_id):
        if g.current_user.collected(discus_id, "discussion"):
            return api_abort(4006, "already collected this item")
        g.current_user.collect(discus_id, "discussion")
        return make_resp("OK")


class DiscussionCollectListAPI(Resource):
    # url: /course/discussions
    method_decorators = [login_required()]

    def get(self):
        key = "user:{}:collect_{}".format(g.current_user.id, "discussion")
        discussion_id_list = list(r.smembers(key))
        discussions = []
        for discussion_id in discussion_id_list:
            discussion_id = discussion_id.decode('utf-8')
            discussion = Discussion.query.get(discussion_id)
            if discussion is not None:
                discussions.append(discussion)

        resp = page_to_json(Discussion, discussions)
        return make_resp(resp)


class DiscussionRecommendAPI(Resource):
    # url: /course/discussions/recommend?count_items=<int>
    method_decorators = [login_required(allowed_anonymous=True)]

    def get(self):
        count = int(request.args.get("count_items", 5))
        discussions = Discussion.query.all()[-1*count:]
        data = Discussion.list_to_json(discussions)
        return make_resp(data)


def register_recourse_discussion(api):
    api.add_resource(DiscussionAPI, "/<int:cid>/discussions/<string:discus_id>")
    api.add_resource(DiscussionListAPI, "/<int:cid>/discussions")
    api.add_resource(CommentAPI, "/<int:cid>/comment/<string:comment_id>")
    api.add_resource(CommentListAPI, "/<int:cid>/discussions/<string:discus_id>/comments")
    api.add_resource(CommentLikeAPI, "/<int:cid>/comment/<string:comment_id>/like")
    api.add_resource(DiscussionCollectAPI, "/<int:cid>/discussions/<string:discus_id>/collect")
    api.add_resource(DiscussionCollectListAPI, "/discussions/collection")
    api.add_resource(DiscussionRecommendAPI, "/discussions/recommend")
