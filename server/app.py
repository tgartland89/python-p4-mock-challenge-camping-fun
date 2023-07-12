# #!/usr/bin/env python3

# PASSING 10 Pytest FAILING 6 
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
    return jsonify(response_data), 201

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

    # Update the camper's name if provided
    if name:
        camper.name = name

    # Update the camper's age if provided and it's a valid integer
    if age:
        try:
            camper.age = int(age)
        except ValueError:
            error_response = {
                'error': 'Invalid age value. Age must be a valid integer.'
            }
            return jsonify(error_response), 400

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

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get(id)

    if not activity:
        error_response = {
            'error': 'Activity not found'
        }
        return jsonify(error_response), 404

# Delete associated signups before deleting the activity
    signups = Signup.query.filter_by(activity_id=id).all()
    for signup in signups:
        db.session.delete(signup)

    db.session.delete(activity)
    db.session.commit()

# Return an empty response body
    return '', 204

@app.route('/signups', methods=['POST'])
def create_signup():
# Get the request body
    request_data = request.get_json()

# Extract the camper_id, activity_id, and time from the request body
    camper_id = request_data.get('camper_id')
    activity_id = request_data.get('activity_id')
    time = request_data.get('time')

# Check if the camper and activity exist
    camper = Camper.query.get(camper_id)
    activity = Activity.query.get(activity_id)

    if not camper or not activity:
        error_response = {
            'error': 'Camper or Activity not found'
        }
        return jsonify(error_response), 404

# Create a new Signup object
    signup = Signup(camper_id=camper_id, activity_id=activity_id, time=time)

# Validate the new signup
    validation_errors = []
    try:
        db.session.add(signup)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        validation_errors = [str(error) for error in e.args]

    if validation_errors:
        response_data = {
            'errors': validation_errors
        }
        return jsonify(response_data), 400

# Create the response data with related activity and camper data
    response_data = {
        'id': signup.id,
        'camper_id': camper.id,
        'activity_id': activity.id,
        'time': signup.time,
        'activity': {
            'id': activity.id,
            'name': activity.name,
            'difficulty': activity.difficulty
        },
        'camper': {
            'id': camper.id,
            'name': camper.name,
            'age': camper.age
        }
    }

# Return the response data as JSON response
    return jsonify(response_data), 201

if __name__ == '__main__':
    app.run(port=5555, debug=True)

# *************************************************************************
# DRY CODE 9 PASS- 7 FAILS

# from models import db, Activity, Camper, Signup
# from flask_restful import Api, Resource
# from flask_migrate import Migrate
# from flask import Flask, make_response, jsonify, request
# import os

# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.json.compact = False

# migrate = Migrate(app, db)
# db.init_app(app)


# def serialize_camper(camper):
#     return {
#         'id': camper.id,
#         'name': camper.name,
#         'age': camper.age
#     }


# def serialize_signup(signup):
#     return {
#         'id': signup.id,
#         'time': signup.time,
#         'activity_id': signup.activity_id
#     }


# def serialize_activity(activity):
#     return {
#         'id': activity.id,
#         'name': activity.name,
#         'difficulty': activity.difficulty
#     }


# def serialize_camper_with_signups(camper):
#     signups = Signup.query.filter_by(camper_id=camper.id).all()
#     signup_data = [serialize_signup(signup) for signup in signups]

#     return {
#         'id': camper.id,
#         'name': camper.name,
#         'age': camper.age,
#         'signups': signup_data
#     }

# # The functions serialize_camper, serialize_signup, and serialize_activity are serialization functions that convert instances of 
# # specific models into dictionaries. These functions extract relevant attributes from the model instances and structure them 
# # as dictionaries for easy serialization to formats like JSON.

# # serialize_camper(camper): This function takes a camper object as input and returns a dictionary representation of the camper 
# # with specific attributes extracted. It extracts the id, name, and age attributes from the camper object and 
# # structures them in a dictionary format.

# # serialize_signup(signup): This function takes a signup object as input and returns a dictionary representation 
# # of the signup. It extracts the id, time, and activity_id attributes from the signup object 
# # and structures them in a dictionary format.

# # serialize_activity(activity): This function takes an activity object as input and returns a dictionary 
# # representation of the activity. It extracts the id, name, and difficulty attributes from the activity 
# # object and structures them in a dictionary format.

# # These serialization functions are used to convert complex objects (instances of models) 
# # into simpler representations (dictionaries) that can be easily serialized and transmitted, 
# # for example, as JSON responses in an API.


# @app.route('/')
# def home():
#     return ''


# @app.route('/campers', methods=['GET'])
# def get_campers():
#     campers = Camper.query.all()
#     camper_data = [serialize_camper(camper) for camper in campers]
#     return jsonify(campers=camper_data)


# @app.route('/campers', methods=['POST'])
# def create_camper():
#     request_data = request.get_json()
#     name = request_data.get('name')
#     age = request_data.get('age')

#     if not age.isdigit():
#         validation_errors = ['Age must be an integer']
#         response_data = {'errors': validation_errors}
#         return jsonify(response_data), 400

#     camper = Camper(name=name, age=int(age))

#     validation_errors = []
#     try:
#         db.session.add(camper)
#         db.session.commit()
#     except ValueError as e:
#         db.session.rollback()
#         validation_errors = [str(error) for error in e.args]

#     if validation_errors:
#         response_data = {'errors': validation_errors}
#         return jsonify(response_data), 400

#     response_data = serialize_camper(camper)
#     return jsonify(response_data), 201



# @app.route('/campers/<int:id>', methods=['GET'])
# def get_camper(id):
#     camper = Camper.query.get(id)

#     if not camper:
#         error_response = {'error': 'Camper not found'}
#         return jsonify(error_response), 404

#     camper_data = serialize_camper_with_signups(camper)
#     return jsonify(camper=camper_data)


# @app.route('/campers/<int:id>', methods=['PATCH'])
# def update_camper(id):
#     camper = Camper.query.get(id)

#     if not camper:
#         error_response = {'error': 'Camper not found'}
#         return jsonify(error_response), 404

#     request_data = request.get_json()
#     name = request_data.get('name')
#     age = request_data.get('age')

#     if name:
#         camper.name = name
#     if age:
#         try:
#             camper.age = int(age)  # Convert age to an integer
#         except ValueError:
#             validation_errors = ['Age must be an integer']
#             response_data = {'errors': validation_errors}
#             return jsonify(response_data), 400

#     validation_errors = []
#     try:
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         validation_errors.append(str(e))

#     if validation_errors:
#         response_data = {'errors': validation_errors}
#         return jsonify(response_data), 400

#     response_data = serialize_camper(camper)
#     return jsonify(response_data)



# @app.route('/activities', methods=['GET'])
# def get_activities():
#     activities = Activity.query.all()
#     activity_data = [serialize_activity(activity) for activity in activities]
#     return jsonify(activity_data)


# @app.route('/activities/<int:id>', methods=['DELETE'])
# def delete_activity(id):
#     activity = Activity.query.get(id)

#     if not activity:
#         error_response = {'error': 'Activity not found'}
#         return jsonify(error_response), 404

#     signups = Signup.query.filter_by(activity_id=id).all()
#     for signup in signups:
#         db.session.delete(signup)

#     db.session.delete(activity)
#     db.session.commit()

#     return '', 204


# @app.route('/signups', methods=['POST'])
# def create_signup():
#     request_data = request.get_json()
#     camper_id = request_data.get('camper_id')
#     activity_id = request_data.get('activity_id')
#     time = request_data.get('time')

#     camper = Camper.query.get(camper_id)
#     activity = Activity.query.get(activity_id)

#     if not camper or not activity:
#         error_response = {'error': 'Camper or Activity not found'}
#         return jsonify(error_response), 404

#     signup = Signup(camper_id=camper_id, activity_id=activity_id, time=time)

#     validation_errors = []
#     try:
#         db.session.add(signup)
#         db.session.commit()
#     except ValueError as e:
#         db.session.rollback()
#         validation_errors = [str(error) for error in e.args]

#     if validation_errors:
#         response_data = {'errors': validation_errors}
#         return jsonify(response_data), 500

#     response_data = {
#         'id': signup.id,
#         'camper_id': camper.id,
#         'activity_id': activity.id,
#         'time': signup.time,
#         'activity': serialize_activity(activity),
#         'camper': serialize_camper(camper)
#     }

#     return jsonify(response_data), 201


# if __name__ == '__main__':
#     app.run(port=5555, debug=True)
