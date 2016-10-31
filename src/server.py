#!/usr/bin/env python
from api import app
from gevent.wsgi import WSGIServer

if __name__ == "__main__":
    try:
        #start server
        http_server = WSGIServer(('0.0.0.0', 8080), app)
        http_server.serve_forever()

    except Exception as e:
        print e