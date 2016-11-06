from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

from api import db
from psycopg2.extras import DictCursor
from api.extensions import requires_auth

user_bp = Blueprint('user_bp', __name__)
user_api = Api(user_bp)

class UserResource(Resource):
    @requires_auth
    def get(self):
        # lookup user
        # note: request.email is set by extensions.requires_auth function
        print request.email
        c = db.cursor(cursor_factory=DictCursor)
        c.execute("SELECT * FROM users WHERE cppemail = %s", (request.email,))

        # shallow copy the result
        row = dict(c.fetchone())
        if row is None:
            return 'User does not exist', 404

        # delete salt and passhash from row
        del row['passhash']
        del row['salt']

        # jsonify row and return
        return jsonify(row)

user_api.add_resource(UserResource, '/')
