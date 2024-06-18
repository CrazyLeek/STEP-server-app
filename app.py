import os, json, datetime

from users import *
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

# The maximum number of journey files the server will store
MAX_JOURNEY_FILES = 1000

# The folder were jouneys are stored
JOURNEYS_FOLDER = "journeys/"

# The password to fetch the journey stored on the server
ADMIN_PASSWORD = "Zélie est une vilaine fille"

app = Flask(__name__)

# Allow CORS
CORS(app)

def journey_list_to_str(journey:list):
    """Convert a journey to a string"""

    MODE, LINE = 0, 1
    res = []

    for trip in journey:
        if trip[MODE] in ("walk", "bike", "car", "dart"):
            res.append(trip[MODE])
        else:
            res.append(trip[MODE] + "-" + trip[LINE])

    return '_'.join(res)

def create_filename_from_journey(journey:list):
    """
    Return a filename describing the journey 
    """

    journey_str = journey_list_to_str(journey)
    date_str = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

    return journey_str + "#" + date_str


def store_file(journey_data):
    """Store a journey data in the hard drive"""

    filename = create_filename_from_journey(journey_data["journey"])

    with open(f"journeys/{filename}.json", 'w') as file:
        json.dump(journey_data, file)


def get_journey_files():
    """Return the dictionnary of all journeys recorded on the server"""

    res = []

    for journey_file in os.listdir(JOURNEYS_FOLDER):

        if journey_file[-5:] == ".json":

            with open(JOURNEYS_FOLDER + journey_file) as file:
                journey = json.load(file)

            res.append(journey)

    return res

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.post("/api/journey_data")
def receive_journey_data():

    if len(os.listdir(JOURNEYS_FOLDER)) < MAX_JOURNEY_FILES:

        store_file(request.get_json())
        return "Data successfully stored on the server", 201
    
    else:
         return "Too many files on the server", 507
    
@app.get("/api/journey_data")
def send_journey_data():

    data = request.get_json()
    res = []

    if not ("password" in data and data["password"] == ADMIN_PASSWORD):
        return "Unauthorized", 401
    

    res = get_journey_files()

    return res

@app.delete("/api/journey_data")
def delete_journey_data():
    """Delete all the journeys stored in the folder"""

    data = request.get_json()

    if not ("password" in data and data["password"] == ADMIN_PASSWORD):
        return "Unauthorized", 401
    

    for filename in os.listdir(JOURNEYS_FOLDER):

        if filename[-5:] == ".json":
            os.remove(JOURNEYS_FOLDER + filename)

    return "Files were successfully deleted"


@app.get('/api/user/<user_id>')
def send_user(user_id):
    """
    API route used to get a user.
    Method:
    - GET
    Possible returns:
    - 200 (OK): Login successful, returns user.
    - 404 (Not Found): Indicates that the requested user was not found.
    - 500 (Internal Server Error): Error fetching user for unknown reason.
    """
    try:
        user = get_user(user_id)
        if user:
            return jsonify({"user": user}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        app.logger.error(f"Error fetching user: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

@app.post("/api/user")
def receive_user():
    """
    API route used to register a new user.
    Method:
    - POST
    Expected JSON request:
        {
            "username": "User name",
            "password": "Password"
        }
    Possible returns:
    - 201 (Created): The user has been created successfully.
    - 400 (Bad Request): The user name already exists in the database.
    - 500 (Internal Server Error): User creation failed for an unknown reason.
    """
    try:
        data = request.json
        username = data.get('username')
        existing_user = get_user_by_username(username)
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400
        user = create_user(data)
        if user:
            return jsonify({"message": "User created successfully", "userId": str(user[0][0])}), 201
        else:
            return jsonify({"error": "Failed to create user"}), 500
    except Exception as e:
        app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

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
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        print(username)
        print(password)
        user = get_user_by_username(username)
        if user and verify_user(username, password):
            user_id = str(user[0][0])
            return jsonify({'userId': user_id}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        app.logger.error(f"Error logging in: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500
    
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
    try:
        if delete_user_by_id(user_id):
            return jsonify({"message": "User and associated data deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete user and associated data"}), 500
    except Exception as e:
        app.logger.error(f"Error deleting user and associated data: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

@app.route("/apps/gps_recorder")
def gps_recorder_page():

    return render_template("gps_record_app.html")


"""
a = rq.get("http://localhost:5000/api/journey_data", json={"password":"Zélie est une vilaine fille"})
aa = json.loads(a.text)

"""