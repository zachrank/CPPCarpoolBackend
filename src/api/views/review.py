from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

from api import db
from psycopg2.extras import RealDictCursor
from api.extensions import requires_auth

review_bp = Blueprint('review_bp', __name__)
review_api = Api(review_bp)

def get_form(key):
    if key not in request.form:
        return None
    return request.form[key]

class ReviewsResource(Resource):
    @requires_auth
    def get(self, param):
        email = param + '@cpp.edu'

        # lookup userid for requested user
        c = db.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT id FROM users WHERE cppemail = %s", (email,))
        # check if we got a result
        row = c.fetchone()
        if row is None:
            return 'User does not exist', 404
        # get id
        userid = dict(row)['id']

        # get all reviews for user, join with users table
        c.execute("SELECT reviews.id, reviews.reviewer_userid, reviews.reviewee_userid, reviews.stars, reviews.content, users.cppemail as reviewer_email, users.fullname as reviewer_name, users.picture as reviewer_picture FROM reviews, users WHERE reviews.reviewee_userid = %s AND reviews.reviewer_userid = users.id", (userid,))

        # check if we got any rows
        rows = c.fetchall()
        if rows is None:
            return jsonify([])

        # jsonify row and return
        return jsonify(results=rows)

    @requires_auth
    def delete(self, param):
        reviewid = int(param)

        # lookup review id and enforce reviewer_userid
        c = db.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT id FROM reviews WHERE reviewer_userid = %s and id = %s", (request.id, reviewid))
        # check if we got a result
        row = c.fetchone()
        if row is None:
            return 'Review does not exist', 404

        # get all reviews for user, join with users table
        c.execute("DELETE FROM reviews WHERE id = %s", (reviewid,))

        return 'OK', 202

class ReviewResource(Resource):
    @requires_auth
    def post(self):
        # make sure user is not reviewing themself
        reviewee_email = get_form('email')
        if reviewee_email == request.email:
            return 'You can not review yourself', 400

        # lookup reviewer id
        c = db.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT id FROM users WHERE cppemail = %s", (request.email,))
        # check if we got a result
        row = c.fetchone()
        if row is None:
            return 'You do not exist', 404
        # get id
        reviewer_id = dict(row)['id']

        # lookup reviewee id
        c.execute("SELECT id FROM users WHERE cppemail = %s", (reviewee_email,))
        # check if we got a result
        row = c.fetchone()
        if row is None:
            return 'User does not exist', 404
        # get id
        reviewee_id = dict(row)['id']

        # make sure user has not already reviewed this person
        c.execute("SELECT id FROM reviews WHERE reviewee_userid = %s and reviewer_userid = %s", (reviewee_id, reviewer_id))
        # check if we got a result
        row = c.fetchone()
        if row is not None:
            return 'You can not review more than once', 400

        # get # of stars
        stars_unparsed = get_form('stars')
        if stars_unparsed is None:
            return 'Missing field: stars', 400
        stars = int(stars_unparsed)
        if stars < 1 or stars > 5:
            return 'Stars out of range', 400

        content = get_form('content')
        if content is None or len(content) == 0:
            return 'Missing field: content', 400

        # insert new record into reviews table
        c.execute("INSERT INTO reviews (reviewer_userid, reviewee_userid, stars, content) VALUES (%s, %s, %s, %s)", (reviewer_id, reviewee_id, stars, content))
        db.commit()

        return 'OK', 201

review_api.add_resource(ReviewsResource, '/<string:param>')
review_api.add_resource(ReviewResource, '/')
