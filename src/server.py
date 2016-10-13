#libraries
import flask
import numpy
import fuzzywuzzy
from fuzzywuzzy import fuzz, process
from flask import Flask, request
from flask_restful import Api
from gevent.wsgi import WSGIServer

#our code
from auth import requires_auth, issue_token, check_login

app = Flask(__name__)
app.config['DEBUG'] = True
api = Api(app)

@app.route('/cartersNumbers/')
def showfirst10():
    a = numpy.arrange(10).reshape(5,2)
    return a

@app.route('/')
def health_check():
    return ('Hello World!', 200)

#endpoint for testing auth
@app.route('/auth')
@requires_auth
def auth_test():
    return ('Ok', 200)

@app.route('/fuwu')
def fuzzthewuzz():
    ratio = fuzz.ratio("fuzz", "wuzz")
    return ratio

@app.route('/login', methods = ['POST'])
def login():
    user = request.form['user']
    password = request.form['password']

    if password is None or user is None:
        return ('Unauthorized.', 401)

    if not check_login(user, password):
        return ('Unauthorized.', 401)

    return issue_token(user)


@app.route('/carter/')
def carter():
    return 'Carter Slocum Was Here'

@app.route('/ztrank/')
def ztrank():
    return 'Is this working?'

if __name__ == '__main__':
    try:
        #start server
        http_server = WSGIServer(('0.0.0.0', 8080), app)
        http_server.serve_forever()

    except Exception as e:
        print e