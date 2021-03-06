from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
import os
import hashlib
import base64
import re
import time
import io
import json
from api.extensions import requires_auth
from api import db, allowed_file
from psycopg2.extras import RealDictCursor
from PIL import Image
from resizeimage import resizeimage

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
        addressline2 = get_form('addressline2') # not required
        city = get_form('city')
        zipcode = get_form('zip')
        schedule = get_form('schedule')
        drivingpref = get_form('drivingpref')
        maxdist = get_form('maxdist')

        # make sure required fields are not missing
        if addressline1 is None or city is None or zipcode is None or schedule is None or drivingpref is None or maxdist is None:
            return 'Missing fields', 400

        # make sure the required fields are not empty
        if len(addressline1) == 0 or len(city) == 0 or len(zipcode) == 0 or len(schedule) == 0 or len(drivingpref) == 0 or len(maxdist) == 0:
            return 'Empty fields', 400

        # write to db
        c = db.cursor(cursor_factory=RealDictCursor)
        c.execute("UPDATE users SET altemail = %s, addressline1 = %s, city = %s, zip = %s, drivingpref = %s, maxdist = %s, profilecomplete = true WHERE id = %s", (altemail, addressline1, city, zipcode, drivingpref, maxdist, request.id))

        schedule = json.loads(schedule)

        # write schedule to db
        for i in range(len(schedule)):
            day = schedule[i]
            c.execute("UPDATE schedule SET arrive = %s, depart = %s WHERE userid = %s AND dayofweek = %s", (day['arrive'], day['depart'], request.id, i,))

        db.commit()

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

        # if no file
        if 'picture' not in request.files:
            return 'Missing file', 400

        # get filename
        picture = request.files['picture']

        # check if the file is one of the allowed filetypes / extensions or empty
        if picture is None or not allowed_file(picture.filename):
            return 'Bad file', 400

        image = Image.open(picture.stream)
        croppedpicture = resizeimage.resize_cover(image, [256, 256])
        imgByteArr = io.BytesIO()
        croppedpicture.save(imgByteArr, format='JPEG')
        imgByteArr = bytearray(imgByteArr.getvalue())

        # write to db
        c = db.cursor(cursor_factory=RealDictCursor)
        c.execute("UPDATE users SET picture = %s WHERE id = %s", (imgByteArr, request.id))
        db.commit()


        return 'OK', 200

settings_api.add_resource(SettingsResource, '/')
settings_api.add_resource(PasswordResource, '/password')
settings_api.add_resource(PictureResource, '/picture')
