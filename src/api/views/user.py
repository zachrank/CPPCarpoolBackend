from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

from api import db
from psycopg2.extras import RealDictCursor
from api.extensions import requires_auth

user_bp = Blueprint('user_bp', __name__)
user_api = Api(user_bp)

class UserResource(Resource):
    @requires_auth
    def get(self, user=None): # default value for user is None
        other_user_email = request.email
        if user is not None:
            other_user_email = user + '@cpp.edu'

        # lookup requested OtherUser
        c = db.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT * FROM users WHERE cppemail = %s", (other_user_email,))

        # check if we got a result
        row = c.fetchone();
        if row is None:
            return 'User does not exist', 404

        # fetch user schedule
        c.execute("SELECT * FROM schedule WHERE userid = %s", (row['id'],))
        schedule = c.fetchall()
        row['schedule'] = [{'arrive': day['arrive'], 'depart': day['depart']} for day in schedule]

        # delete salt and passhash from row
        del row['passhash']
        del row['salt']

        # check if requestinguser != otheruser. If so, remove exact location info
        # note: request.email is set by extensions.requires_auth function
        if request.email != other_user_email:
            del row['addressline1']
            del row['addressline2']

        # jsonify row and return
        return jsonify(row)

user_api.add_resource(UserResource, '/', '/<string:user>')
