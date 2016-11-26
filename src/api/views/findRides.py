from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from api import db
from psycopg2.extras import RealDictCursor
from api.extensions import issue_token
from api.extensions import requires_auth
from api import maps

findRides_bp = Blueprint('findRides_bp', __name__)
findRides_api = Api(findRides_bp)

class RidesResource(Resource):
    @requires_auth
    def get(self):
        c = db.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT * FROM users WHERE cppemail = %s", (request.email,))
        # check if we got a result
        row = c.fetchone();
        if row is None:
            return 'User does not exist', 404
        # load user location info
        user = (request.email, row['addressline1'] + ' ' + row['city'] + ', ' + str(row['zip']))

        # load all other users
        c.execute("SELECT * FROM users WHERE cppemail != %s AND verified = true AND profilecomplete = true", (request.email,))
        rows = c.fetchall()

        for row in rows:
            del row['passhash']
            del row['salt']

        sortedResults = maps.sortByDist(user, rows)
        sortedUsers = []
        for res in sortedResults:
            res[0]['dist'] = res[1]
            del res[0]['addressline1']
            del res[0]['addressline2']
            sortedUsers.append(res[0])

        for user in sortedUsers:
            # fetch reviews
            c.execute("SELECT * FROM reviews WHERE reviewee_userid = %s", (user['id'],))
            rows = c.fetchall()

            # compute average num of stars
            starsList = list(map(lambda r: r['stars'], rows))
            stars = reduce(lambda sum, s: sum + s, starsList) / len(rows)

            # add on review count and avg stars
            user['reviewCount'] = len(rows)
            user['stars'] = stars

        return jsonify(results=sortedUsers)

findRides_api.add_resource(RidesResource, '/')
