from flask import Flask, request, make_response, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        all_msgs = [msg.to_dict() for msg in Message.query.order_by('created_at').all()]
        return all_msgs, 200
    else:
        try:
            data = request.get_json()
            # new_msg = Message(
            #     body = data.get('body'),
            #     username = data.get('username')
            # )
            new_msg = Message(**data) #! Model validations might fail
            db.session.add(new_msg)
            db.session.commit() #! db constraints might fail
            return new_msg.to_dict(), 201
        except:
            db.session.rollback()
            return {'error': 'Something went wrong :('}, 400

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    if request.method == 'PATCH':
        try:
            data = request.get_json()
            if msg := db.session.get(Message, id):
                for k, v in data.items():
                    setattr(msg, k, v)
                db.session.commit()
                return msg.to_dict(), 200
            return {'error': f'No message {id} found'}
            # abort(404, f'No message {id} found')
        except:
            db.session.rollback()
            return {'error': 'Something went wrong :('}, 400
    else:
        try:
            if msg := db.session.get(Message, id):
                db.session.delete(msg)
                db.session.commit()
                return {}, 204
            return {'error': f'No message {id} found'}
        except:
            db.session.rollback()
            return {'error': 'Something went wrong :('}, 400


if __name__ == '__main__':
    app.run(port=5555)
