import redis
from flask import g, session, current_app
from flask_socketio import join_room, leave_room, disconnect

from app.extensions import socketio, pool
from app.modules import User, Course


def join_room_(data):
    # ["nickname", "cid"]
    room = "room:" + str(data['cid'])
    join_room(room)
    socketio.emit("join_room", data['nickname'], room=room)


def leave_room_(data):
    room = "room:" + str(data['cid'])
    leave_room(room)
    socketio.emit("leave_room", data["nickname"], room=room)


def send_message(data):
    # ["content", "uid", "cid", "content"]
    room = "room:" + str(data['cid'])
    message = dict()
    message['content'] = data['content']
    user = User.query.get(int(data['uid']))
    message['user'] = user.to_json()
    socketio.emit("send_message", message, room=room)


def join_personal_room(data):
    user = g.current_user
    room = "user:{}".format(user.id)
    join_room(room)
    socketio.emit("join_personal_room", "succeed", room=room)


def get_system_tips(data):
    user = g.current_user
    room = "user:{}".format(user.id)
    key = "system_tips:{}".format(user.id)
    r = redis.Redis(connection_pool=pool)
    msgs = list(r.smembers(key))
    socketio.emit("system_tips", msgs, room=room)


# def on_connect(data):
#     token = get_token(data)
#     validate_token(token)
#     user = load_token(token)
#     join_room_("user:{}".format(user.id))
#     session['uid'] = user.id
#     socketio.emit("connect", "OK")


# def login_required(f):
#     def decorator(*args, **kws):
#         with current_app.context():
#             user = User.query.get(session['uid'])
#             g.current_user = user
#             return f(*args, **kws)
#     return decorator


# def join_course_required(f):
#     @login_required
#     def decorator(*args, **kwargs):
#         with current_app.context():
#             data = args[0]
#             cid = data['cid']
#             course = Course.query.get(cid)
#             if not g.current_user.is_teacher and not g.current_user.is_student(course):
#                 disconnect()
#             return f(*args, **kwargs)
#     return decorator


socketio.on_event("join_room", join_room_)
socketio.on_event("leave_room", leave_room_)
socketio.on_event("send_message", send_message)
socketio.on_event("join_personal_room", join_personal_room)
socketio.on_event("get_system_tips", get_system_tips)
