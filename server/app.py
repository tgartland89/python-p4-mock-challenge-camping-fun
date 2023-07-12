#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


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

# Create a list to hold camper data
    camper_data = []

# Iterate over each camper and extract the required fields
    for camper in campers:
        camper_info = {
            'id': camper.id,
            'name': camper.name,
            'age': camper.age
        }
        camper_data.append(camper_info)

# Return the camper data as JSON response
    return jsonify(campers=camper_data)


@app.route('/campers', methods=['POST'])
def create_camper():
    # Get the request body
    request_data = request.get_json()

    # Extract the name and age from the request body
    name = request_data.get('name')
    age = request_data.get('age')

    # Create a new Camper object
    camper = Camper(name=name, age=age)

    # Validate the new camper
    validation_errors = []
    try:
        db.session.add(camper)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        validation_errors = [str(error) for error in e.args]

    if validation_errors:
        response_data = {
            'errors': validation_errors
        }
        return jsonify(response_data), 400

    # Create the response data
    response_data = {
        'id': camper.id,
        'name': camper.name,
        'age': camper.age
    }

    # Return the response data as JSON response
    return jsonify(response_data), 20

@app.route('/campers/<int:id>', methods=['GET'])
def get_camper(id):
    camper = Camper.query.get(id)

    if not camper:
        error_response = {
            'error': 'Camper not found'
        }
        return jsonify(error_response), 404

    # Get the camper's signups
    signups = Signup.query.filter_by(camper_id=id).all()

    # Create a list to hold signup data
    signup_data = []

    # Iterate over each signup and extract the required fields
    for signup in signups:
        signup_info = {
            'id': signup.id,
            'time': signup.time,
            'activity_id': signup.activity_id
        }
        signup_data.append(signup_info)

    # Create the camper data with signups
    camper_data = {
        'id': camper.id,
        'name': camper.name,
        'age': camper.age,
        'signups': signup_data
    }

    # Return the camper data as JSON response
    return jsonify(camper=camper_data)


@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = Camper.query.get(id)

    if not camper:
        error_response = {
            'error': 'Camper not found'
        }
        return jsonify(error_response), 404

    # Get the request body
    request_data = request.get_json()

    # Extract the name and age from the request body
    name = request_data.get('name')
    age = request_data.get('age')

    # Update the camper's name and age if provided
    if name:
        camper.name = name
    if age:
        camper.age = age

    # Validate the updated camper
    validation_errors = []
    try:
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        validation_errors = [str(error) for error in e.args]

    if validation_errors:
        response_data = {
            'errors': validation_errors
        }
        return jsonify(response_data), 400

    # Create the response data
    response_data = {
        'id': camper.id,
        'name': camper.name,
        'age': camper.age
    }

    # Return the response data as JSON response
    return jsonify(response_data)

@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()

    # Create a list to hold activity data
    activity_data = []

    # Iterate over each activity and extract the required fields
    for activity in activities:
        activity_info = {
            'id': activity.id,
            'name': activity.name,
            'difficulty': activity.difficulty
        }
        activity_data.append(activity_info)

    # Return the activity data as JSON response
    return jsonify(activity_data)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
