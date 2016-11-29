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

class ConversationResource(Resource):
    @requires_auth
    def get(self, other_email):
        if other_email is None:
            return 'Missing other_email', 400

        # lookup userid for requested user
        c = db.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT id FROM users WHERE cppemail = %s", (other_email + '@cpp.edu',))
        # check if we got a result
        row = c.fetchone()
        if row is None:
            return 'User does not exist', 404
        # get id
        other_id = row['id']

        # lookup message history
        c.execute("SELECT * FROM messages WHERE receive_userid = %s and send_userid = %s or receive_userid = %s and send_userid = %s ORDER BY timestamp ASC", (other_id, request.id, request.id, other_id))

        messages = c.fetchall()
        for m in messages:
            m['outgoing'] = m['send_userid'] == request.id

        # mark as read in db
        c.execute("UPDATE messages SET read = true WHERE receive_userid = %s and send_userid = %s", (request.id, other_id))
        db.commit()

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

class ConversationsResource(Resource):
    @requires_auth
    def get(self):
        # lookup user's entire message histroy
        c = db.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT * FROM messages WHERE receive_userid = %s or send_userid = %s ORDER BY timestamp DESC", (request.id, request.id))

        rows = c.fetchall()
        if rows is None or len(rows) == 0:
            return jsonify(results=[])

        conversations = {}
        order = []

        for m in rows:
            is_sender = False
            other_id = m['send_userid']
            if other_id == request.id:
                is_sender = True
                other_id = m['receive_userid']

            if other_id not in conversations:
                order.append(other_id)
                conversations[other_id] = { 'id': other_id, 'lastmessage': m, 'unread': 0 }

                # fetch picture and name. Slow, but works for demo
                c.execute("SELECT picture, fullname, cppemail FROM users WHERE id = %s", (other_id,))
                row = c.fetchone();
                if row is not None:
                    if row['picture'] is not None:
                        conversations[other_id]['picture'] = row['picture']
                    if row['fullname'] is not None:
                        conversations[other_id]['fullname'] = row['fullname']
                    if row['cppemail'] is not None:
                        conversations[other_id]['cppemail'] = row['cppemail']
            else:
                if m['timestamp'] > conversations[other_id]['lastmessage']['timestamp']:
                    conversations[other_id]['lastmessage'] = m

            if not is_sender and not m['read']:
                conversations[other_id]['unread'] += 1

        results_sorted = []
        for conv_id in order:
            results_sorted.append(conversations[conv_id])

        return jsonify(results=results_sorted)

messages_api.add_resource(ConversationsResource, '/conversations')
messages_api.add_resource(ConversationResource, '/', '/<string:other_email>')
