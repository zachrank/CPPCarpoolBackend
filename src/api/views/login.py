from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
import os
import hashlib
import base64
import re

from api import db
from psycopg2.extras import DictCursor
from api.extensions import issue_token

login_bp = Blueprint('login_bp', __name__)
login_api = Api(login_bp)

def get_form(key):
    if key not in request.form:
        return None
    return request.form[key]

class LoginResource(Resource):
    def post(self):
        email = get_form('email')
        password = get_form('password')

        # make sure required fields are not empyty
        if email is None or password is None:
            return 'Bad request', 400

        # lookup user
        c = db.cursor(cursor_factory=DictCursor)
        c.execute("SELECT * FROM users WHERE cppemail = %s", (email,))
        # shallow copy the result
        row = dict(c.fetchone())
        if row is None:
            return 'User does not exist', 401

        # check password
        passhash = hashlib.sha256(password + row['salt']).hexdigest()

        if passhash != row['passhash']:
            return 'Bad password', 401

        del row['passhash']
        del row['salt']

        row['token'] = issue_token(row['cppemail'])

        return jsonify(row)

class PasswordResource(Resource):
    def post(self):
        return 'fg', 200

class CheckResource(Resource):
    #check to see if user with email already exists
    def post(self):
        email = get_form('email')

        if email is None:
            return 'Bad request', 400

        c = db.cursor(cursor_factory=DictCursor)
        c.execute("SELECT id, fullname FROM users WHERE cppemail = %s", (email,))
        row = c.fetchone()

        if row is None:
            return 'User does not exist', 404

        return jsonify(row)

class RegisterResource(Resource):
    #register a new user
    def post(self):
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

        # make sure user doesn't already exist
        c = db.cursor()
        c.execute("SELECT id FROM users WHERE cppemail = %s", (email,))
        if c.fetchone() is not None:
            return 'Bad request', 400

        # salt and hash password
        salt = os.urandom(32).encode('hex')
        passhash = hashlib.sha256(password + salt).hexdigest()

        # write to db
        c.execute("INSERT INTO users (cppemail, fullname, altemail, salt, passhash) VALUES (%s, %s, %s, %s, %s)", (email, fullname, alt, salt, passhash))
        db.commit()

        return 'OK', 200

login_api.add_resource(LoginResource, '/')
login_api.add_resource(PasswordResource, '/forgot')
login_api.add_resource(RegisterResource, '/register')
login_api.add_resource(CheckResource, '/check')
