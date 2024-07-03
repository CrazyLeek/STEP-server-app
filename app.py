import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from users import *
from journeys import *
from auth import *

# The maximum number of journey files the server will store
MAX_JOURNEY_FILES = 1000

# The folder where journeys are stored
JOURNEYS_FOLDER = "journeys/"

# The password to fetch the journey stored on the server
ADMIN_PASSWORD = "Zélie est une vilaine fille"

app = Flask(__name__)

# Allow CORS
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.post("/api/journey_data/new")
def receive_journey_data_new():
    """
    API route used to store new journey data.
    Method:
        - POST
    Expected JSON request:
        Journey data in JSON format.
    Possible returns:
        - 201 (Created): Data successfully stored.
        - 507 (Insufficient Storage): Too many files on the server.
    """
    return store_journey_file(request.get_json())

@app.post("/api/journey_data")
def receive_journey_data():
    """
    API route used to store journey data.
    Method:
        - POST
    Expected JSON request:
        Journey data in JSON format.
    Possible returns:
        - 201 (Created): Data successfully stored.
        - 507 (Insufficient Storage): Too many files on the server.
    """
    if len(os.listdir(JOURNEYS_FOLDER)) < MAX_JOURNEY_FILES:
        store_file(request.get_json())
        return "Data successfully stored on the server", 201
    else:
        return "Too many files on the server", 507

@app.get("/api/journey_data")
def send_journey_data():
    """
    API route used to get all journey data.
    Method:
        - GET
    Expected JSON request:
        {
            "password": "Admin password"
        }
    Possible returns:
        - 200 (OK): Data retrieved successfully.
        - 401 (Unauthorized): Invalid password.
    """
    data = request.get_json()
    if not ("password" in data and data["password"] == ADMIN_PASSWORD):
        return "Unauthorized", 401
    return jsonify(get_journey_files())

@app.delete("/api/journey_data")
def delete_journey_data():
    """
    API route used to delete all journey data.
    Method:
        - DELETE
    Expected JSON request:
        {
            "password": "Admin password"
        }
    Possible returns:
        - 200 (OK): Files deleted successfully.
        - 401 (Unauthorized): Invalid password.
    """
    data = request.get_json()
    if not ("password" in data and data["password"] == ADMIN_PASSWORD):
        return "Unauthorized", 401
    return delete_all_journey_files()

@app.post("/api/login")
def receive_login():
    """
    API route used to connect a user.
    Method:
        - POST
    Expected JSON request:
        {
            "username": "User name",
            "password": "Password"
        }
    Possible returns:
        - 200 (OK): Login successful, returns user ID.
        - 401 (Unauthorized): Invalid credentials.
        - 500 (Internal Server Error): Connection attempt error for unknown reason.
    """
    return login_user(request.json)

@app.get('/api/user/<user_id>')
def send_user(user_id):
    """
    API route used to get a user.
    Method:
        - GET
    Possible returns:
        - 200 (OK): User details retrieved successfully.
        - 404 (Not Found): User not found.
        - 500 (Internal Server Error): Error fetching user for unknown reason.
    """
    return get_user_details(user_id)

@app.post("/api/user")
def receive_user():
    """
    API route used to register a new user.
    Method:
        - POST
    Expected JSON request:
        {
            "username": "User name",
            "firstName": "First name",
            "lastName": "Last name",
            "password": "Password"
        }
    Possible returns:
        - 201 (Created): The user has been created successfully.
        - 400 (Bad Request): The user name already exists in the database.
        - 500 (Internal Server Error): User creation failed for an unknown reason.
    """
    return register_user(request.json)

@app.delete('/api/user/<user_id>')
def delete_user(user_id):
    """
    API route for deleting a specific user and all associated data.
    Method:
        - DELETE
    URL parameters:
        - user_id: ID of the user to be deleted
    Possible returns:
        - 200 (OK): User deleted successfully.
        - 500 (Internal Server Error): Error when deleting the user or their data for an unknown reason.
    """
    return remove_user(user_id)

@app.get("/api/journey/user/<user_id>")
def send_journeys(user_id):
    """
    API route used to get all journeys for a specific user.
    Method:
        - GET
    URL parameters:
        - user_id: ID of the user whose journeys are to be fetched.
    Possible returns:
        - 200 (OK): Journeys retrieved successfully.
        - 404 (Not Found): No journeys found for the given user ID.
        - 500 (Internal Server Error): Error retrieving journeys.
    """
    return get_user_journeys(user_id)

@app.post("/api/journey")
def receive_journey():
    """
    API route used to receive and store a new journey.
    Method:
        - POST
    Expected JSON request:
        {
            "userId": 1,
            "name": "Journey name",
            "methodsJson": NEED TO CONFIRM THE STRUCTURE
        }
    Possible returns:
        - 201 (Created): Journey created successfully.
        - 400 (Bad Request): Invalid input data.
        - 500 (Internal Server Error): Error creating journey.
    """
    return store_journey(request.json)

@app.get("/api/specification/method/<method_id>")
def send_specifications_method(method_id):
    """
    API route used to get specifications for a specific method.
    Method:
        - GET
    URL parameters:
        - method_id: ID of the method whose specifications are to be fetched.
    Possible returns:
        - 200 (OK): Specifications retrieved successfully.
        - 404 (Not Found): No specifications found for the given method ID.
        - 500 (Internal Server Error): Error retrieving specifications.
    """
    return get_method_specifications(method_id)

@app.get("/api/method/<method_id>")
def send_method(method_id):
    """
    API route used to get details of a specific method.
    Method:
        - GET
    URL parameters:
        - method_id: ID of the method to be fetched.
    Possible returns:
        - 200 (OK): Method details retrieved successfully.
        - 404 (Not Found): No method found with the given ID.
        - 500 (Internal Server Error): Error retrieving method details.
    """
    return get_method_details(method_id)

@app.get("/api/journey/<journey_id>")
def send_journey(journey_id):
    """
    API route used to get details of a specific journey.
    Method:
        - GET
    URL parameters:
        - journey_id: ID of the journey to be fetched.
    Possible returns:
        - 200 (OK): Journey details retrieved successfully.
        - 404 (Not Found): No journey found with the given ID.
        - 500 (Internal Server Error): Error retrieving journey details.
    """
    return get_journey_details(journey_id)

@app.post("/api/record")
def receive_record():
    """
    API route used to receive and store a new journey record.
    Method:
        - POST
    Expected JSON request:
        {
            "journeyId": 1,
            "isValidated": false,
            "isPending": true
        }
    Possible returns:
        - 201 (Created): Record created successfully.
        - 500 (Internal Server Error): Error creating record.
    """
    return store_record(request.json)

@app.get("/api/methods_with_specifications")
def send_methods_with_specifications():
    """
    API route used to get all methods with their specifications.
    Method:
        - GET
    Possible returns:
        - 200 (OK): Methods and specifications retrieved successfully.
        - 500 (Internal Server Error): Error retrieving methods and specifications.
    """
    return get_all_methods_with_specifications()

@app.delete('/api/journey/<journey_id>')
def delete_journey(journey_id):
    """
    API route used to delete a specific journey.
    Method:
        - DELETE
    URL parameters:
        - journey_id: ID of the journey to be deleted.
    Possible returns:
        - 200 (OK): Journey deleted successfully.
        - 404 (Not Found): No journey found with the given ID.
        - 500 (Internal Server Error): Error deleting the journey.
    """
    return remove_journey(journey_id)

@app.route("/apps/gps_recorder")
def gps_recorder_page():
    return render_template("gps_record_app.html")

@app.route("/apps/step")
def step_app_page():
    return render_template("step_app.html")

if __name__ == '__main__':
    app.run(debug=True)