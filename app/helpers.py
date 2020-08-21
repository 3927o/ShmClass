import time
import redis
import xlrd
from hashlib import md5
from flask import jsonify, Flask, g, current_app
from werkzeug.exceptions import NotFound

from .extensions import pool


class AppDispatcher(Flask):
    prefix_app_map = dict()

    def __call__(self, environ, start_response):
        current_app = self.full_dispatch_app(environ)

        return current_app(environ, start_response)

    def full_dispatch_app(self, environ):
        path_info = environ["PATH_INFO"]

        current_app = self.dispatch_app(environ, path_info)
        if current_app is None:
            current_app = NotFound()

        return current_app

    def dispatch_app(self, environ, path_info):
        current_app = None

        for prefix in self.prefix_app_map:
            if path_info.find(prefix) == 0:
                environ["PATH_INFO"] = path_info.replace(prefix, "")

                if environ["PATH_INFO"] == "":
                    environ["PATH_INFO"] = "/"

                current_app = self.prefix_app_map[prefix]
                break

        return current_app

    def register_app(self, app, prefix):

        if prefix in self.prefix_app_map:
            raise ValueError("An application already be registered by prefix \"{}\".".format(prefix))

        self.prefix_app_map[prefix] = app


def guess_type(url):
    media_type = None

    types = ['picture', 'video', 'audio', 'word', 'excel', 'ppt', 'pdf', 'python', 'cpp']
    picture = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'ico']
    video = ['mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv']
    audio = ['mp3', 'wma', 'ape', 'flac']
    word = ['doc', 'docx', 'docm', 'dotx', 'dotm']
    excel = ['xls', 'xlsx', 'xlsm', 'xltx', 'xltm', 'xlsb', 'xlam']
    ppt = ['ppt', 'pptx', 'pptm', 'ppsx', 'ppsm', 'potx', 'potm', 'ppam']
    pdf = ['pdf']
    python = ['py']
    cpp = ['cpp', 'c']

    d = dict()
    for type_ in types:
        d[type_] = eval(type_)

    postfix = url.split('.')[-1].lower()
    for k, v in d.items():
        if postfix in v:
            media_type = k
            break

    if media_type is None:
        raise RuntimeError("unsupported type or missing postfix")

    return media_type


def edit_module(module, data):
    for k in data:
        if data[k] is not None:
            setattr(module, k, data[k])


def api_abort(code, message=None, **kwargs):

    response = jsonify(status=code, message=message, **kwargs)
    response.status_code = 200

    return response


def make_resp(data, status=2000, message='succeed'):
    resp = jsonify({
        'status': status,
        'message': message,
        'data': data
    })
    resp.status_code = 200
    return resp


def format_time(ts):
    return time.strftime("%Y/%m/%d %X", time.localtime(ts))


def strptime(str_time):
    return time.mktime(time.strptime(str_time, "%Y/%m/%d %X"))


def push_url_builder(stream_name, time,
                     key="1b74cb987121964596c61e9176ba1e72", domain="rtmp://102433.livepush.myqcloud.com/live/"):
    txTime = hex(int(strptime(time)))[2:].upper()
    txSecret = md5((key+stream_name+txTime).encode("utf-8")).hexdigest()
    stream = "{}?txSecret={}&txTime={}".format(stream_name, txSecret, txTime)
    return domain + stream


def get_current_course(resource_name):
    course = None
    if hasattr(g, "current_course"):
        course = g.current_course
    else:
        resource = getattr(g, "current_{}".format(resource_name))
        course = resource.course

    return course


def validate_verify_code(code_type, code, email_or_phone):
    # use for test
    if code == "666666":
        return True

    action = current_app.config["CODE_TYPE"][code_type]
    key = "VerifyCode:{}:{}".format(action, email_or_phone)
    r = redis.Redis(connection_pool=pool)
    true_code = r.get(key)
    return code == true_code


def parse_excel(request, filename, transform=True):

    file = request.files[filename]
    f = file.stream.read()
    data = xlrd.open_workbook(file_contents=f)
    table = data.sheets()[0]
    col_name = table.row_values(0)
    li = list()

    for i in range(1, table.nrows):  # iterate the rows
        d = dict()
        row_values = table.row_values(i)

        for j in range(table.ncols):
            key = col_name[j]
            d[key] = row_values[j]

        if transform:
            d = excel_column_transformer(d)

        li.append(d)
    return li


def excel_column_transformer(data):
    transformer = {
        "学校": "school",
        "学号": "student_id",
        "姓名": "name",
        "教师id": "teacher_id",
        "认证码": "certificate_code",
        "年级": "grade",
        "班级": "class_"
    }
    d = dict()
    for key in data:
        if key in transformer:
            en_key = transformer[key]
            d[en_key] = data[key]
    d["certificate_code"] = str(int(d["certificate_code"]))
    return d

