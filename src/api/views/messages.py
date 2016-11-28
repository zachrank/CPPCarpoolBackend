from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from api import db
from psycopg2.extras import RealDictCursor
from api.extensions import requires_auth

messages_bp = Blueprint('messages_bp', __name__)
messages_api = Api(messages_bp)

def get_form(key):
    if key not in request.form:
        return None
    return request.form[key]

class MessagesResource(Resource):
    @requires_auth
    def get(self, other_email):
        c = db.cursor(cursor_factory=RealDictCursor)
        messages = []

        if other_email is not None:
            # fetch one conversation

            # lookup userid for requested user
            c.execute("SELECT id FROM users WHERE cppemail = %s", (other_email + '@cpp.edu',))
            # check if we got a result
            row = c.fetchone()
            if row is None:
                return 'User does not exist', 404
            # get id
            other_id = row['id']

            # lookup message history
            c.execute("SELECT * FROM messages WHERE receive_userid = %s and send_userid = %s or receive_userid = %s and send_userid = %s ORDER BY timestamp ASC", (other_id, request.id, request.id, other_id))
        else:
            # fetch all conversations
            c.execute("SELECT * FROM messages WHERE receive_userid = %s or send_userid = %s ORDER BY timestamp ASC", (other_id, request.id))

        messages = c.fetchall()
        for m in messages:
            m['outgoing'] = m['send_userid'] == request.id

        return jsonify(results=messages)

    @requires_auth
    def post(self):
        to_userid = get_form('to_userid')
        text = get_form('message')

        # make sure required fields are not empyty
        if to_userid is None or text is None:
            return 'Missing fields', 400

        # write to db
        c = db.cursor(cursor_factory=RealDictCursor)
        c.execute("INSERT INTO messages (send_userid, receive_userid, message, timestamp) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)", (request.id, to_userid, text))
        db.commit()

        return 'OK', 200

messages_api.add_resource(MessagesResource, '/', '/<string:other_email>')
