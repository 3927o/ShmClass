from flask_restful.reqparse import RequestParser


course_create_reqparser = RequestParser()
course_create_reqparser.add_argument('name', type=str, required=True)
course_create_reqparser.add_argument('public', type=int, required=True)
course_create_reqparser.add_argument('introduce', type=str)
course_create_reqparser.add_argument('start_at', type=float, required=True)
course_create_reqparser.add_argument('end_at', type=float, required=True)

course_put_reqparser = RequestParser()
course_put_reqparser.add_argument("introduce", type=str, location="json")
course_put_reqparser.add_argument("start_at", type=float, location="json")
course_put_reqparser.add_argument("end_at", type=float, location="json")

upload_reqparser = RequestParser()
upload_reqparser.add_argument('chapter_id', type=str, required=True)
upload_reqparser.add_argument('name', type=str, required=True)
upload_reqparser.add_argument("media_type", type=str, required=True, choices=("document", "movie"))

media_list_reqparser = RequestParser()
media_list_reqparser.add_argument("media_type", type=str, required=True, choices=("document", "movie"))

chapter_create_reqparser = RequestParser()
chapter_create_reqparser.add_argument("chapter_name", type=str, required=True)

discussion_create_reqparser = RequestParser()
discussion_create_reqparser.add_argument('content', type=str, required=True, location='json')

comment_reqparser = RequestParser()
comment_reqparser.add_argument('content', type=str, required=True, location='json')
comment_reqparser.add_argument('reply', type=str, required=False, location='json')

notice_create_reqparser = RequestParser()
notice_create_reqparser.add_argument('title', type=str, required=True, location='json')
notice_create_reqparser.add_argument('content', type=str, required=True, location='json')

commit_create_reqparser = RequestParser()
commit_create_reqparser.add_argument("expires", type=int, required=True, location="json")
