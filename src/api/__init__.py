from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)
db = psycopg2.connect("dbname='cppc' user='postgres' host='cppcarpool-db' password=''")

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

#these modules are dependent on (app or db) so they must be imported down here
from views.login import login_bp

# Register views
app.register_blueprint(login_bp, url_prefix='/login')
