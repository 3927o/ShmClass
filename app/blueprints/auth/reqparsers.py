from flask_restful.reqparse import RequestParser


signup_reqparser = RequestParser()
signup_reqparser.add_argument('nickname', required=True, type=str, location='json')
signup_reqparser.add_argument('email', required=True, type=str, location='json')
signup_reqparser.add_argument('password', required=True, type=str, location='json')
signup_reqparser.add_argument('code', required=True, type=str, location='json')

login_reqparser = RequestParser()
login_reqparser.add_argument('method', type=int, required=True)

tel_login_reqparser = RequestParser()
tel_login_reqparser.add_argument('mail', type=str, required=True)
tel_login_reqparser.add_argument('code', type=str, required=True)

pwd_login_reqparser = RequestParser()
pwd_login_reqparser.add_argument('username', type=str, required=True)
pwd_login_reqparser.add_argument('password', type=str, required=True)

verify_code_reqparser = RequestParser()
verify_code_reqparser.add_argument('type', type=int, required=True, location='json')
verify_code_reqparser.add_argument('email', type=str, required=True, location='json')

user_del_reqparser = RequestParser()
user_del_reqparser.add_argument("verify_code", type=str, required=True, location="json")

reset_pwd_reqparser = RequestParser()
reset_pwd_reqparser.add_argument("verify_code", type=str, required=True, location="json")
reset_pwd_reqparser.add_argument("new_pwd", type=str, required=True, location="json")

reset_email_reqparser = RequestParser()
reset_email_reqparser.add_argument("new_email", type=str, required=True, location="json")
reset_email_reqparser.add_argument("new_email_code", type=str, required=True, location="json")
reset_email_reqparser.add_argument("old_email_code", type=str, required=True, location="json")
