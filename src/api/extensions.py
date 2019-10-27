import flask
import jwt
from flask import Response, request, make_response
from datetime import datetime, timedelta
from functools import wraps

jwt_key = ""
with open('secrets/jwt.key', 'r') as key:
    jwt_key = key.read()

jwt_token_duration = 24 * 60  # 24 hour tokens


# generate a new token
def issue_token(id, email):
    utcnow = datetime.utcnow()
    new_token = jwt.encode(
        {
            'id': id,
            'email': email,
            'iat': utcnow,
            'exp': utcnow + timedelta(
                minutes=jwt_token_duration)
        },
        jwt_key,
        algorithm='HS512'
    )

    return new_token


def requires_auth(api_method):
    def bad_request():
        return Response('Bad Request.', 400)

    def unauthorized():
        return Response('Unauthorized.', 401)

    # logic to handle the different possible responses
    # http://flask.pocoo.org/docs/0.10/quickstart/#about-responses
    def parseResp(resp):
        if isinstance(resp, flask.wrappers.ResponseBase):
            return resp

        if type(resp) is str:
            return make_response(resp)

        if type(resp) is tuple:
            if type(resp[0]) is not str:
                resp = (json.dumps(resp[0]),) + resp[1:]

            return make_response(resp)

        return make_response(json.dumps(resp))

    @wraps(api_method)
    def check_auth(*args, **kwargs):
        # Get auth header
        try:
            auth_header = request.headers["Authorization"]
        except KeyError:
            print "No auth header"
            return unauthorized()

        # Extract token from auth header
        auth_split = auth_header.split(' ', 1)

        if len(auth_split) != 2:
            logger.info("Missing token")
            return unauthorized()

        scheme = auth_split[0]
        payload = auth_split[1]

        if scheme != 'Bearer':
            print "Bad auth scheme: " + scheme
            return unauthorized()

        try:
            # decode token
            decoded_token = jwt.decode(payload, jwt_key, algorithms=['HS512'], verify=True)

            # add email and id to request object
            request.id = decoded_token['id']
            request.email = decoded_token['email']

            # create new token
            utcnow = datetime.utcnow()
            new_token = jwt.encode(
                {
                    'id': decoded_token['id'],
                    'email': decoded_token['email'],
                    'iat': utcnow,
                    'exp': utcnow + timedelta(
                        minutes=jwt_token_duration)
                },
                jwt_key,
                algorithm='HS512')

            # wrap the original api method
            resp = parseResp(api_method(*args, **kwargs))

            # Inject new token
            resp.headers["Renew-Token"] = new_token

            return resp
        except jwt.ExpiredSignatureError:
            print "Expired token"
            return unauthorized()
        except jwt.InvalidTokenError:
            print "Token decode error"
            return unauthorized()

    return check_auth
