from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

from api.picture import resizeimage
from api.extensions import requires_auth

from api import db
from psycopg2.extras import RealDictCursor

settings_bp = Blueprint('settings_bp', __name__)
settings_api = Api(settings_bp)


def get_form(key):
    if key not in request.form:
        return None
    return request.form[key]


class SettingsResource(Resource):
	# modify a user's profile
	@requires_auth
	def post(self):
		altemail = get_form('altemail')
		addressline1 = get_form('addressline1')
		addressline2 = get_form('addressline2')
		city = get_form('city')
		zip = get_form('zip')
		# schedule = #array[7] of tuples[3]
		drivingpref = get_form('drivingpref')
		maxdist = get_form('maxdist')

		# make sure required fields are not empty
		if altemail is None or addressline1 is None or addressline2 is None or city is None or zip is None or drivingpref is None or maxdist is None:
			return 'Missing fields', 400

			c = db.cursor(cursor_factory=RealDictCursor)
			c.execute("INSERT INTO users (altemail, addressline1, addressline2, city, zip, drivingpref, maxdist) VALUES (%s, %s, %s, %s, %s, %s, %s)",
			(altemail, addressline1, addressline2, city, zip, drivingpref, maxdist))
			db.commit()

	# delete user account
	@requires_auth
	def delete(self):
		c = db.cursor(cursor_factory=RealDictCursor)
		c.execute("DELETE FROM users WHERE id = %s", (request.id,))
		c.execute("DELETE FROM reviews WHERE reviewer_userid = %s OR reviewee_userid = %s", (request.id, request.id,))
		c.execute("DELETE FROM schedule WHERE userid = %s", (request.id,))
		c.execute("DELETE FROM interaction WHERE user1 = %s OR user2 = %s", (request.id, request.id,))


class PasswordResource(Resource):
	# reset user password
	@requires_auth
	def post(self):
		oldpassword = get_form('oldpassword')
		newpassword = get_form('newpassword')

		# make sure required fields are not empty
		if oldpassword is None or newpassword is None:
			return 'Missing fields', 400

			# salt password
			c = db.cursor(cursor_factory=RealDictCursor)
			c.execute("SELECT * FROM users WHERE cppemail = %s", (request.email,))
			salt = os.urandom(32).encode('hex')
			passhash = hashlib.sha256(newpassword + salt).hexdigest()

			# write to db
			c.execute("INSERT INTO users (salt, passhash) VALUES (%s, %s)", (salt, passhash))
			db.commit()

			return 'OK', 200


class PictureResource(Resource):
	# upload new profile picture
	@requires_auth
	def post(self):
		# might need to convert from base64 encoding prior to getting the form
		picture = resizeimage(get_form('profilepicture'))

		# make sure required fields are not empty
		if picture is None:
			return 'Missing fields', 400

			# write to db
			c = db.cursor(cursor_factory=RealDictCursor)
			c.execute("INSERT INTO users (picture) VALUES (%s)", (picture))
			db.commit()

			return 'OK', 200

settings_api.add_resource(SettingsResource, '/')
settings_api.add_resource(PasswordResource, '/password')
settings_api.add_resource(PictureResource, '/picture')
