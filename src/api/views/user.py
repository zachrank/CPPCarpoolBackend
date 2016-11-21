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
        c = db.cursor(cursor_factory=DictCursor)
        c.execute("SELECT * FROM users WHERE cppemail = %s", (request.email,))

        # check if we got a result
        row = c.fetchone();
        if row is None:
            return 'User does not exist', 404

        #shallow copy result
        row = dict(row)

        # delete salt and passhash from row
        del row['passhash']
        del row['salt']

        # jsonify row and return
        return jsonify(row)

class OtherUserResource(Resource):
    @requires_auth
    def get(self, user):
        # lookup requested OtherUser
        other_user_email = user + '@cpp.edu'
        c = db.cursor(cursor_factory=DictCursor)
        c.execute("SELECT * FROM users WHERE cppemail = %s", (other_user_email,))

        # check if we got a result
        row = c.fetchone();
        if row is None:
            return 'User does not exist', 404

        #shallow copy result
        row = dict(row)

        # delete salt and passhash from row
        del row['passhash']
        del row['salt']

        # check if requesting user != otheruser. If so, remove exact location info
        # note: request.email is set by extensions.requires_auth function
        if request.email != other_user_email:
            del row['addressline1']
            del row['addressline2']
            # del row['city']
            # del row['zip']

        # jsonify row and return
        return jsonify(row)

user_api.add_resource(UserResource, '/')
user_api.add_resource(OtherUserResource, '/<string:user>')
