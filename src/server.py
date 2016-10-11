import flask
from flask import Flask
from flask_restful import Api
from gevent.wsgi import WSGIServer

app = Flask(__name__)
api = Api(app)


@app.route('/')
def health_check():
    return ('Hello World!', 200)

@app.route('/carter/')
def carter():
    return 'Carter Slocum Was Here'

if __name__ == '__main__':
    try:
        #start server
        http_server = WSGIServer(('0.0.0.0', 8080), app)
        http_server.serve_forever()

    except Exception as e:
        print e
