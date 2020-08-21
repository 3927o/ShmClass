from flask_restful.reqparse import RequestParser


teacher_put_reqparser = RequestParser()
teacher_put_reqparser.add_argument("introduce", type=str, location="json")
teacher_put_reqparser.add_argument("gender", type=str, location="json")

teacher_certificate_reqparser = RequestParser()
teacher_certificate_reqparser.add_argument('school', required=True, type=str, location='json')
teacher_certificate_reqparser.add_argument('role_id', required=True, type=str, location='json')
teacher_certificate_reqparser.add_argument('certificate_code', required=True, type=str, location='json')