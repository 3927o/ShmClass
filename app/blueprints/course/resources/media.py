import pickle
from flask import g, request
from flask_restful import Resource

from app.interceptors import resource_found_required, role_required
from app.helpers import make_resp, api_abort
from app.modules import Chapter, Media, page_to_json
from app.extensions import db

from ..reqparsers import upload_reqparser, media_list_reqparser, chapter_create_reqparser


class ChapterListAPI(Resource):
    # url: /course/<int:cid>/chapters
    method_decorators = {
        "get": [role_required("student", "course"), resource_found_required('course')],
        "post": [role_required("teacher", "course"), resource_found_required("course")],
        "delete": [role_required("teacher", "course"), resource_found_required("course")]
    }

    def get(self, cid):
        chapters = g.current_course.chapters
        resp = page_to_json(Chapter, chapters)
        return make_resp(resp)

    def post(self, cid):
        chapter_name = chapter_create_reqparser.parse_args()["chapter_name"]
        new_chapter = Chapter(chapter_name)
        new_chapter.course = g.current_course
        db.session.add(new_chapter)
        db.session.commit()
        return make_resp("OK")


class MediaAPI(Resource):
    # url: /course/media/<string:media_id>
    method_decorators = [resource_found_required("media")]

    def get(self, media_id):
        resp = g.current_media.to_json()
        return make_resp(resp)


class MediaUploadAPI(Resource):
    # url: /course/<int:cid>/medias/upload
    method_decorators = [role_required("teacher", "course"), resource_found_required('course'),
                         resource_found_required("chapter")]

    def post(self, cid):
        # expected str chapter and file document, if chapter not exist, create it.
        data = upload_reqparser.parse_args()
        name = data['name']
        media_type = data["media_type"]

        # get new media
        media = request.files.get('media')
        if media is None:
            return api_abort(4002, "media is None")

        # save new media
        new_media = Media.save_media(media, 'course/{}/{}'.format(g.current_course.id, media_type),
                                     name=name, return_model=True)

        # update chapter's media list
        new_media_uuid = new_media.id
        chapters_media = getattr(g.current_chapter, media_type + "s")
        media_uuid_list = pickle.loads(chapters_media)
        media_uuid_list.append(new_media_uuid)
        chapters_media = pickle.dumps(media_uuid_list)
        setattr(g.current_chapter, media_type + "s", chapters_media)

        db.session.commit()
        resp = new_media.to_json()
        return make_resp(resp)


class MediaListAPI(Resource):
    # url: /course/<int:cid>/medias
    method_decorators = [role_required("student", "course"), resource_found_required('course')]

    def get(self, cid):
        media_type = media_list_reqparser.parse_args()["media_type"]
        chapters = g.current_course.chapters

        if media_type == "document":
            resp = page_to_json(Chapter, chapters, with_documents=True)
        else:
            resp = page_to_json(Chapter, chapters, with_movies=True)

        return make_resp(resp)


class ChapterMediaListAPI(Resource):
    # url: /course/<int:cid>/medias/<string:chapter_id>
    method_decorators = [role_required("student", "course"),
                         resource_found_required("course"), resource_found_required("chapter")]

    def get(self):
        if g.current_chapter not in g.current_course.chapters:
            return api_abort(4003, "chapter not in the course")

        media_type = media_list_reqparser.add_argument()["media_type"]
        resp = g.current_chapter.to_json(with_mediatype=True)
        return make_resp(resp)


def register_recourse_media(api):
    api.add_resource(ChapterListAPI, '/<int:cid>/chapters', endpoint="chapters")
    api.add_resource(MediaAPI, '/media/<string:media_id>', endpoint="media")
    api.add_resource(MediaUploadAPI, '/<int:cid>/medias/upload')
    api.add_resource(MediaListAPI, '/<int:cid>/medias')
