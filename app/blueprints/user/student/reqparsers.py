from flask_restful.reqparse import RequestParser


student_put_reqparser = RequestParser()
student_put_reqparser.add_argument("nickname", type=str, location="json")
student_put_reqparser.add_argument("introduce", type=str, location="json")
student_put_reqparser.add_argument("gender", type=str, location="json")

stu_certificate_reqparser = RequestParser()
stu_certificate_reqparser.add_argument('school', required=True, type=str, location='json')
stu_certificate_reqparser.add_argument('student_id', required=True, type=str, location='json')
stu_certificate_reqparser.add_argument('certificate_code', required=True, type=str, location='json')