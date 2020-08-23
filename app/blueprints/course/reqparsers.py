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
