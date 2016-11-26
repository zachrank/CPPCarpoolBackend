from flask import Flask, jsonify
from flask.json import JSONEncoder
import psycopg2
import calendar
from datetime import datetime

app = Flask(__name__)
db = psycopg2.connect("dbname='cppc' user='postgres' host='cppcarpool-db' password=''")

# custom json encoder to convert dates to iso 8601 format
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
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

app.config['DEBUG'] = True

# these modules are dependent on (app or db) so they must be imported down here
from views.login import login_bp
from views.user import user_bp
from views.review import review_bp
from views.findRides import findRides_bp
from views.settings import settings_bp
import maps

# Register views
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(review_bp, url_prefix='/review')
app.register_blueprint(findRides_bp, url_prefix='/findRides')
app.register_blueprint(settings_bp, url_prefix='/settings')
