from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

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
        return jsonify(maps.getNearbyUsers((request.email, row['addressline1'])))

    

findRides_api.add_resource(RidesResource, '/')