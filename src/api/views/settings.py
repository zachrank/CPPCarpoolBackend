from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
import os
import hashlib
import base64
import re
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
		zipcode = get_form('zip')
		# schedule = #array[7] of tuples[3]
		drivingpref = get_form('drivingpref')
		maxdist = get_form('maxdist')

		# make sure required fields are not empty
		if altemail is None or addressline1 is None or addressline2 is None or city is None or zipcode is None or drivingpref is None or maxdist is None:
			return 'Missing fields', 400

		c = db.cursor(cursor_factory=RealDictCursor)
		c.execute("UPDATE users SET altemail = %s, addressline1 = %s, addressline2 = %s, city = %s, zip = %s, drivingpref = %s, maxdist = %s WHERE id = %s", (altemail, addressline1, addressline2, city, zipcode, drivingpref, maxdist, request.id))
		db.commit()
		c.execute("SELECT * FROM users WHERE id = %s" (request.id,))
		print c.fetchone()

		return "OK", 200

	# delete user account
	@requires_auth
	def delete(self):
		c = db.cursor(cursor_factory=RealDictCursor)
		c.execute("DELETE FROM users WHERE id = %s", (request.id,))
		c.execute("DELETE FROM reviews WHERE reviewer_userid = %s OR reviewee_userid = %s", (request.id, request.id,))
		c.execute("DELETE FROM schedule WHERE userid = %s", (request.id,))
		c.execute("DELETE FROM interaction WHERE user1 = %s OR user2 = %s", (request.id, request.id,))

		return "OK", 202


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
		c.execute("UPDATE users SET salt = %s, passhash = %s WHERE id = %s", (salt, passhash, request.id))
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
