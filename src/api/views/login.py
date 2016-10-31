from flask import Blueprint, request
from flask_restful import Api, Resource
import os
import hashlib
import base64
import re

from api import db

login_bp = Blueprint('login_bp', __name__)
login_api = Api(login_bp)

class LoginResource(Resource):
    def post(self):
        return 'login', 200

class PasswordResource(Resource):
    def post(self):
        return 'fg', 200


class RegisterResource(Resource):
    def post(self):
        def get_form(key):
            if key not in request.form:
                return None
            return request.form[key]

        email = get_form('email')
        alt = get_form('altemail')
        password = get_form('password')
        fullname = get_form('name')

        # make sure required fields are not empyty
        if email is None or password is None or fullname is None or len(fullname) == 0:
            return 'Bad request', 400

        # use regex to enforce .cpp email
        if re.match(r'^[a-zA-Z]+@cpp\.edu$', email) is None:
            return 'Bad request', 400

        # salt and hash password
        salt = os.urandom(32).encode('hex')
        passhash = hashlib.sha256(password + salt).hexdigest()

        # write to db
        c = db.cursor()
        c.execute("INSERT INTO users (cppemail, fullname, altemail, salt, passhash) VALUES (%s, %s, %s, %s, %s)", (email, fullname, alt, salt, passhash))
        db.commit()

        return 'OK', 200


login_api.add_resource(LoginResource, '')
login_api.add_resource(PasswordResource, '/forgot')
login_api.add_resource(RegisterResource, '/register')
