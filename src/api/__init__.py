from flask import Flask, jsonify, request, redirect, url_for
from flask.json import JSONEncoder
import psycopg2
import calendar
from datetime import datetime, time
import base64
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'bmp', 'tif', 'gif'])

app = Flask(__name__)
db = psycopg2.connect("dbname='cppc' user='postgres' host='cppcarpool-db' password=''")

# custom json encoder to convert dates to iso 8601 format
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, buffer):
                return base64.b64encode(obj)

            if isinstance(obj, time):
                return "{:02d}:{:02d}:{:02d}".format(obj.hour, obj.minute, obj.second)

            if isinstance(obj, datetime):
                if obj.utcoffset() is not None:
                    obj = obj - obj.utcoffset()
                isodate = obj.isoformat()
                return isodate

            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Not found."}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"message": "Bad request."}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"message": "Unauthorized."}), 401

@app.route('/')
def health_check():
    return ('OK', 200)

# @app.before_request
# def kill_time():
#     import time
#     # sleep for 250ms
#     time.sleep(.25)


app.config['DEBUG'] = True

# these modules are dependent on (app or db) so they must be imported down here
from views.login import login_bp
from views.user import user_bp
from views.review import review_bp
from views.search import search_bp
from views.settings import settings_bp
import maps

# Register views
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(review_bp, url_prefix='/review')
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(settings_bp, url_prefix='/settings')
