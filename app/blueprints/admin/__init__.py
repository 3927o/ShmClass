from flask import Blueprint
from flask_restful import Api


def create_admin_bp(name="admin_bp"):
    admin_bp = Blueprint(name, __name__)

    register_api(admin_bp)

    return admin_bp


def register_api(app):
    api = Api(app)

    return api
