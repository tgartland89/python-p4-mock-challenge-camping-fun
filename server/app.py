from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route('/')
def home():
    return ''


@app.route('/campers', methods=['GET'])
def get_campers():
    campers = Camper.query.all()
    camper_data = [serialize_camper(camper) for camper in campers]
    return jsonify(campers=camper_data)


@app.route('/campers', methods=['POST'])
def create_camper():
    request_data = request.get_json() or {}
    name = request_data.get('name', '')
    age = request_data.get('age')

    if not age.isdigit():
        validation_errors = ['Age must be an integer']
        response_data = {'errors': validation_errors}
        return jsonify(response_data), 400

    camper = Camper(name=name, age=int(age))

    validation_errors = []
    try:
        db.session.add(camper)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        validation_errors = [str(error) for error in e.args]

    if validation_errors:
        response_data = {'errors': validation_errors}
        return jsonify(response_data), 400

    response_data = {
        'id': camper.id,
        'name': camper.name,
        'age': camper.age
    }

    return jsonify(response_data), 201


@app.route('/campers/<int:id>', methods=['GET'])
def get_camper(id):
    camper = Camper.query.get(id)

    if not camper:
        error_response = {'error': 'Camper not found'}
        return jsonify(error_response), 404

    camper_data = serialize_camper_with_signups(camper)
    return jsonify(camper=camper_data)


@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = Camper.query.get(id)

    if not camper:
        error_response = {'error': 'Camper not found'}
        return jsonify(error_response), 404

    request_data = request.get_json()
    name = request_data.get('name')
    age = request_data.get('age')

    if name:
        camper.name = name
    if age:
        try:
            camper.age = int(age)  # Convert age to an integer
        except ValueError:
            error_response = {
                'error': 'Invalid age value. Age must be a valid integer.'
            }
            return jsonify(error_response), 400

    validation_errors = []
    try:
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        validation_errors = [str(error) for error in e.args]

    if validation_errors:
        response_data = {'errors': validation_errors}
        return jsonify(response_data), 400

    response_data = {
        'id': camper.id,
        'name': camper.name,
        'age': camper.age
    }

    return jsonify(response_data), 202


@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    activity_data = [serialize_activity(activity) for activity in activities]
    return jsonify(activity_data)


@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get(id)

    if not activity:
        error_response = {'error': 'Activity not found'}
        return jsonify(error_response), 404

    signups = Signup.query.filter_by(activity_id=id).all()
    for signup in signups:
        db.session.delete(signup)

    db.session.delete(activity)
    db.session.commit()

    return '', 204


@app.route('/signups', methods=['POST'])
def create_signup():
    request_data = request.get_json()
    camper_id = request_data.get('camper_id')
    activity_id = request_data.get('activity_id')
    time = request_data.get('time')

    camper = Camper.query.get(camper_id)
    activity = Activity.query.get(activity_id)

    if not camper or not activity:
        error_response = {'error': 'Camper or Activity not found'}
        return jsonify(error_response), 400

    if not isinstance(time, int) or time < 0 or time > 23:
        error_response = {
            'error': 'Invalid time value. Time must be between 0 and 23.'
        }
        return jsonify(error_response), 400

    signup = Signup(camper_id=camper_id, activity_id=activity_id, time=time)

    validation_errors = []
    try:
        db.session.add(signup)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        validation_errors = [str(error) for error in e.args]

    if validation_errors:
        response_data = {'errors': validation_errors}
        return jsonify(response_data), 400

    response_data = {
        'id': signup.id,
        'camper_id': camper.id,
        'activity_id': activity.id,
        'time': signup.time,
        'activity': serialize_activity(activity),
        'camper': serialize_camper(camper)
    }

    return jsonify(response_data), 201


def serialize_camper(camper):
    return {
        'id': camper.id,
        'name': camper.name,
        'age': camper.age
    }


def serialize_signup(signup):
    return {
        'id': signup.id,
        'time': signup.time,
        'activity_id': signup.activity_id
    }


def serialize_activity(activity):
    return {
        'id': activity.id,
        'name': activity.name,
        'difficulty': activity.difficulty
    }


def serialize_camper_with_signups(camper):
    signups = Signup.query.filter_by(camper_id=camper.id).all()
    signup_data = [serialize_signup(signup) for signup in signups]

    return {
        'id': camper.id,
        'name': camper.name,
        'age': camper.age,
        'signups': signup_data
    }


if __name__ == '__main__':
    app.run(port=5555, debug=True)
