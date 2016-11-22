from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from api import db
from psycopg2.extras import DictCursor
from api.extensions import issue_token
from api.extensions import requires_auth
from api import maps

findRides_bp = Blueprint('findRides_bp', __name__)
findRides_api = Api(findRides_bp)

class RidesResource(Resource):
    @requires_auth
    def post(self):
        c = db.cursor(cursor_factory=DictCursor)
        c.execute("SELECT * FROM users WHERE cppemail = %s", (request.email,))
        # check if we got a result
        row = c.fetchone();
        if row is None:
            return 'User does not exist', 404
        # shallow copy result
        row = dict(row)
        user = (request.email, row['addressline1'])
        d = db.cursor(cursor_factory=DictCursor)
        d.execute("SELECT * FROM users WHERE cppemail != %s", (request.email,))
        users = []
        for i in range(c.rowcount()):
            row = c.fetchone()
            # shallow copy result
            row = dict(row)
            del row['passhash']
            del row['salt']
            users.append(row)
        sortedUsers = maps.sortByDist(user,users)
        sortedJ = []
        for x in sortedUsers:
            x[0]['dist'] = x[1]
            del x[0]['addressline1']
            del x[0]['addressline2']
            sortedJ.append(x[0])
        return jsonify(sortedJ)

findRides_api.add_resource(RidesResource, '/')