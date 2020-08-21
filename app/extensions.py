from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from flask_apscheduler import APScheduler
from celery import Celery
import redis

db = SQLAlchemy()
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=False)
socketio = SocketIO(cors_allowed_origins="*")
mail = Mail()
toolbar = DebugToolbarExtension()
cors = CORS()
celery = Celery()
scheduler = APScheduler()


def celery_init_app(celery_, app):
    celery_.main = app.name
    celery_.conf.update(app.config)


def register_extensions(app):
    db.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    toolbar.init_app(app)
    cors.init_app(app)
    celery_init_app(celery, app)
    scheduler.init_app(app)
