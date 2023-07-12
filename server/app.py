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

@app.route('/campers/<int:id>', methods=['GET'])
def get_camper(id):
    camper = Camper.query.get(id)

    if not camper:
        (404)  # Return a 404 error if the camper doesn't exist

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


if __name__ == '__main__':
    app.run(port=5555, debug=True)
