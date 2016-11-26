from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
import os
import hashlib
import base64
import re
from datetime import datetime

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

        # check if we got a result
        row = c.fetchone()
        if row is None:
            return 'User does not exist', 404
        # shallow copy result
        row = dict(row)

        # check password
        passhash = hashlib.sha256(password + row['salt']).hexdigest()

        if passhash != row['passhash']:
            return 'Bad password', 401

        del row['passhash']
        del row['salt']

        row['token'] = issue_token(row['id'], row['cppemail'])

        return jsonify(row)

class PasswordResource(Resource):
    def post(self):
        return 'fg', 200

class CheckResource(Resource):
    # check to see if user with email already exists
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
    # register a new user
    def post(self):
        email = get_form('email')
        alt = get_form('altemail')
        password = get_form('password')
        fullname = get_form('fullname')

        # make sure required fields are not empyty
        if email is None or password is None or fullname is None or len(fullname) == 0:
            return 'Missing fields', 400

        # use regex to enforce .cpp email
        if re.match(r'^[a-zA-Z]+@cpp\.edu$', email) is None:
            return 'cpp email', 400

        # make sure user doesn't already exist
        c = db.cursor()
        c.execute("SELECT id FROM users WHERE cppemail = %s", (email,))
        if c.fetchone() is not None:
            return 'account exists', 400

        # salt and hash password
        salt = os.urandom(32).encode('hex')
        passhash = hashlib.sha256(password + salt).hexdigest()

        verified = True # TODO: implement email verification

        # write to db
        c.execute("INSERT INTO users (cppemail, fullname, altemail, salt, passhash, verified, timestamp) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING id", (email, fullname, alt, salt, passhash, verified))
        userid = c.fetchone()[0]
        values = []
        for day in range(7):
            values.append(userid)
            values.append(day)

        # write empty schedule to db
        c.execute("INSERT INTO schedule (userid, dayofweek) VALUES (%s, %s), (%s, %s), (%s, %s), (%s, %s), (%s, %s), (%s, %s), (%s, %s)", tuple(values))
        db.commit()

        return 'OK', 200

login_api.add_resource(LoginResource, '/')
login_api.add_resource(PasswordResource, '/forgot')
login_api.add_resource(RegisterResource, '/register')
login_api.add_resource(CheckResource, '/check')
